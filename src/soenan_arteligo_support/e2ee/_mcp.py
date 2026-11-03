from __future__ import annotations

import json
from collections.abc import Callable
from contextlib import asynccontextmanager
from functools import partial
from typing import Any, Literal

import anyio
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.fastmcp.tools.base import Tool
from mcp.types import CallToolResult, TextContent, Tool as MCPTool
from pydantic import ValidationError
from soenan.arteligo.application.v1 import application_pb2 as app
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto

from ..transfer import TransferError, upload_file, upload_wav_preview
from ..transfer._workflow import _download_to_stream
from ._crypto import E2eeError
from ._directory import EncryptedDirectory
from ._file_boundary import FileBoundary
from ._local_broker import LocalBrokerClient, LocalGrantHandle, MemoryGrant
from ._mcp_conversations import register_conversation_tools
from ._records import EncryptedRecords
from ._session import DeviceSession
from ._signed_commands import AcceptedCommand


_READ_TOOLS = frozenset({
    "arteligo_list_projects", "arteligo_read_records", "arteligo_read_changes",
    "arteligo_read_current", "arteligo_get_records", "arteligo_list_folder",
    "arteligo_download_file", "arteligo_chat_messages", "arteligo_chat_events",
    "arteligo_chat_message", "arteligo_chat_message_history", "arteligo_chat_operation",
    "arteligo_comment_threads", "arteligo_comment_thread", "arteligo_comment_replies",
    "arteligo_comment_reply",
})
_UPDATE_TOOLS = frozenset({
    "arteligo_write_record", "arteligo_delete_record", "arteligo_upload_file",
    "arteligo_upload_wav_preview", "arteligo_chat_send", "arteligo_chat_edit",
    "arteligo_chat_delete", "arteligo_comment_create", "arteligo_comment_reply_create",
    "arteligo_comment_edit", "arteligo_comment_reply_edit", "arteligo_comment_resolution",
    "arteligo_delete_file", "arteligo_delete_preview",
})


class _OperationRegistry:
    def __init__(self, grant: MemoryGrant):
        self.grant = grant
        self.tools: dict[str, Tool] = {}

    def tool(self):
        def register(function):
            if function.__name__ not in _READ_TOOLS | _UPDATE_TOOLS:
                raise ValueError("unclassified_local_operation")
            tool = Tool.from_function(function)
            if tool.is_async:
                raise ValueError("async_local_operation")
            self.tools[function.__name__] = tool
            return function
        return register

    def describe(self) -> list[dict[str, Any]]:
        self.grant.require_active()
        return [
            MCPTool(
                name=tool.name, description=tool.description, inputSchema=tool.parameters,
                outputSchema=tool.output_schema,
            ).model_dump(mode="json", by_alias=True, exclude_none=True)
            for name, tool in self.tools.items()
            if self.grant.access == "update" or name in _READ_TOOLS
        ]

    def invoke(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        self.grant.require_active()
        if not isinstance(name, str) or name not in self.tools:
            raise E2eeError("operation_not_granted")
        tool = self.tools[name]
        try:
            model = tool.fn_metadata.arg_model
            if not isinstance(arguments, dict) or set(arguments) - model.model_fields.keys():
                raise E2eeError("invalid_tool_arguments")
            parsed = model.model_validate(arguments, strict=True)
            values = parsed.model_dump_one_level()
            if name != "arteligo_list_projects":
                self.grant.authorize(values["project_id"], update=name in _UPDATE_TOOLS)
            result = tool.fn(**values)
            converted = (
                result if isinstance(result, CallToolResult)
                else tool.fn_metadata.convert_result(result)
            )
            if isinstance(converted, CallToolResult):
                response = converted
            elif isinstance(converted, tuple):
                content, structured = converted
                response = CallToolResult(content=content, structuredContent=structured)
            else:
                response = CallToolResult(content=converted)
            return response.model_dump(mode="json", by_alias=True, exclude_none=True)
        except ValidationError:
            raise E2eeError("invalid_tool_arguments") from None
        except ToolError as error:
            raise E2eeError(str(error)) from None
        except TransferError as error:
            raise E2eeError(error.code) from None
        except (KeyError, TypeError, ValueError, OSError):
            raise E2eeError("invalid_content_or_transport") from None


class _GrantedMCP(FastMCP):
    def __init__(self, handle: LocalGrantHandle):
        self._broker_client = LocalBrokerClient(handle)

        @asynccontextmanager
        async def lifespan(_):
            try:
                yield {}
            finally:
                self.close_grant()

        super().__init__(
            "Arteligo granted local tools",
            instructions=(
                "Only the human-approved projects and access level are available. "
                "File paths are relative to the separate granted input and output directories. "
                "The broker alone holds OAuth credentials and device and project keys. "
                "Login, device admission, key replacement, approval, project creation, and grant "
                "expansion require the human-operated CLI or ordinary application. "
                "Closing this connection or expiry rejects new operations and drains accepted work. "
                "A disconnected update may already have committed. Do not assume it was reverted."
            ),
            lifespan=lifespan,
        )

    def close_grant(self) -> None:
        self._broker_client.close()

    async def list_tools(self) -> list[MCPTool]:
        try:
            tools = await anyio.to_thread.run_sync(
                partial(self._broker_client.request, "list_tools"), abandon_on_cancel=True,
            )
            return [MCPTool.model_validate(tool) for tool in tools]
        except E2eeError as error:
            raise ToolError(error.code) from None
        except BaseException:
            self.close_grant()
            raise

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> CallToolResult:
        try:
            result = await anyio.to_thread.run_sync(
                partial(self._broker_client.request, "call_tool", name=name, arguments=arguments),
                abandon_on_cancel=True,
            )
            return CallToolResult.model_validate(result)
        except E2eeError as error:
            raise ToolError(error.code) from None
        except BaseException:
            self.close_grant()
            raise


def create_local_mcp(grant: LocalGrantHandle) -> _GrantedMCP:
    if not isinstance(grant, LocalGrantHandle):
        raise E2eeError("local_grant_required")
    return _GrantedMCP(grant)


def _public_file_metadata(metadata):
    value = {
        "file_id": metadata.file_id, "name": metadata.name,
        "media_type": metadata.media_type, "plaintext_size": metadata.plaintext_size,
        "created_by_user_id": metadata.created_by_user_id,
        "created_at": metadata.created_at, "updated_at": metadata.updated_at,
        "object_id": metadata.original.object_id,
    }
    if metadata.HasField("preview"):
        preview = metadata.preview
        value["preview"] = {
            "preview_id": preview.preview_id, "source_object_id": preview.source_object_id,
            "profile": preview.profile, "codec": preview.codec, "filename": preview.filename,
            "media_type": preview.media_type, "duration_seconds": preview.duration_seconds,
            "sample_rate": preview.sample_rate, "channels": preview.channels,
            "object_id": preview.object.object_id, "state": preview.state,
        }
    return value


def _public_result(value):
    if isinstance(value, crypto.KeyRef):
        return {"id": value.id, "generation": value.generation}
    if isinstance(value, list):
        return [_public_result(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = dict(value)
    kind = result.get("kind")
    if isinstance(result.get("value"), bytes) and kind == "file_metadata":
        result["value"] = _public_file_metadata(app.FileMetadata.FromString(result["value"]))
    elif isinstance(result.get("value"), bytes) and kind in {"file_upload", "file_preview_upload"}:
        message = app.FileUploadDraft if kind == "file_upload" else app.PreviewUploadDraft
        draft = message.FromString(result["value"])
        result["value"] = {"draft_id": draft.draft_id, "metadata": _public_file_metadata(draft.metadata)}
        if kind == "file_upload":
            result["value"]["state"] = draft.state
    return {key: _public_result(item) for key, item in result.items()}


def _broker_operations(
    session: DeviceSession, grant: MemoryGrant, files: FileBoundary
) -> _OperationRegistry:
    server = _OperationRegistry(grant)

    def run(operation: Callable[[DeviceSession], Any]) -> Any:
        try:
            session.require_approved()
            result = operation(session)
            if isinstance(result, AcceptedCommand):
                saved = result.result
                facts = {"state": "saved", "local_result": "unavailable"}
                for name in ("organization_id", "project_id", "device_id", "object_id"):
                    if name in saved:
                        facts[name] = saved[name]
                if "records" in saved:
                    facts["record_ids"] = [record["record_id"] for record in saved["records"]]
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(facts))], isError=True)
            return _public_result(result)
        except E2eeError as error:
            raise ToolError(error.code) from None
        except TransferError as error:
            raise ToolError(error.code) from None
        except (KeyError, TypeError, ValueError, OSError):
            raise ToolError("invalid_content_or_transport") from None

    @server.tool()
    def arteligo_list_projects() -> dict[str, Any]:
        """List only the explicitly granted projects using their current account authorization."""
        def selected(session):
            projects = []
            cursor = ""
            while True:
                result = session.catalog(cursor=cursor)
                projects.extend(project for project in result["projects"] if project["project_id"] in grant.projects)
                if not result["has_more"]:
                    return {"projects": projects}
                if result["cursor"] == cursor:
                    raise E2eeError("invalid_response")
                cursor = result["cursor"]

        return run(selected)

    @server.tool()
    def arteligo_read_records(
        project_id: str, after: int = 0, limit: int = 128
    ) -> dict[str, Any]:
        """Read one authenticated, decrypted change page; pass its cursor for the next page."""
        return run(
            lambda session: EncryptedRecords(session).page(
                project_id, after=after, limit=limit
            )
        )

    @server.tool()
    def arteligo_read_changes(
        project_id: str, after: int = 0, limit: int = 256
    ) -> dict[str, Any]:
        """Read bounded invalidations; fetch selected records to verify their current content."""
        return run(
            lambda session: EncryptedRecords(session).changes(
                project_id, after=after, limit=limit
            )
        )

    @server.tool()
    def arteligo_read_current(
        project_id: str,
        kind: str | None = None,
        after_record_id: str | None = None,
        limit: int = 256,
    ) -> dict[str, Any]:
        """Read one bounded current-record page; filtering names and paths stays on this computer."""
        return run(
            lambda session: EncryptedRecords(session).current(
                project_id, kind=kind, after_record_id=after_record_id, limit=limit
            )
        )

    @server.tool()
    def arteligo_get_records(project_id: str, record_ids: list[str]) -> dict[str, Any]:
        """Read and decrypt selected opaque record IDs without reading the project."""
        return run(
            lambda session: EncryptedRecords(session).read(project_id, record_ids)
        )

    @server.tool()
    def arteligo_list_folder(
        project_id: str,
        folder_id: str | None = None,
        limit: int = 100,
        cursor: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Read one decrypted folder page in name order; a changed folder invalidates its cursor."""
        return run(
            lambda session: EncryptedDirectory(
                EncryptedRecords(session), project_id
            ).page(folder_id=folder_id, limit=limit, cursor=cursor)
        )

    @server.tool()
    def arteligo_write_record(
        project_id: str,
        record_id: str,
        kind: Literal[
            "project",
            "directory",
            "submission",
            "comment",
            "chat",
            "stage",
            "schedule",
        ],
        expected_revision: int,
        value: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Encrypt and sign a record update; a revision conflict requires rereading the current record."""
        if kind in {"chat", "comment"}:
            raise ToolError("conversation_operation_required")
        return run(
            lambda session: EncryptedRecords(session).write(
                project_id,
                records=[
                    {
                        "record_id": record_id,
                        "kind": kind,
                        "expected_revision": expected_revision,
                        "value": value,
                    }
                ],
            )
        )

    @server.tool()
    def arteligo_delete_record(
        project_id: str,
        record_id: str,
        kind: Literal["project", "directory", "submission", "stage", "schedule"],
        expected_revision: int,
    ) -> list[dict[str, Any]]:
        """Sign a metadata-only deletion marker; no document is encrypted or retained in the marker."""
        return run(
            lambda session: EncryptedRecords(session).write(
                project_id,
                records=[{
                    "record_id": record_id,
                    "kind": kind,
                    "expected_revision": expected_revision,
                    "deleted": True,
                }],
            )
        )

    def delete_file_content(session, project_id, file_id, expected_revision, *, preview_only):
        records = EncryptedRecords(session)
        current = records.read(project_id, [file_id]).get(file_id)
        if current is None or current["deleted"] or current["kind"] != "file_metadata":
            raise E2eeError("file_not_found")
        if current["revision"] != expected_revision:
            raise E2eeError("revision_conflict")
        metadata = app.FileMetadata.FromString(current["value"])
        deleted = []
        if metadata.HasField("preview"):
            deleted.append(metadata.preview.object.object_id)
        if preview_only:
            if not metadata.HasField("preview"):
                raise E2eeError("preview_not_found")
            metadata.ClearField("preview")
            draft = {"record_id": file_id, "kind": "file_metadata", "expected_revision": expected_revision,
                "value": metadata.SerializeToString()}
            binding = app.FileRevisionBinding(file_id=file_id, revision=expected_revision + 1,
                metadata_value_id=file_id, metadata_revision=expected_revision + 1,
                original_object_id=metadata.original.object_id)
        else:
            deleted.append(metadata.original.object_id)
            draft = {"record_id": file_id, "kind": "file_metadata", "expected_revision": expected_revision, "deleted": True}
            binding = app.FileRevisionBinding(file_id=file_id, revision=expected_revision + 1,
                metadata_value_id=file_id, metadata_revision=expected_revision + 1)
        return records.write(project_id, records=[draft], deleted_objects=deleted, files=[binding])

    @server.tool()
    def arteligo_delete_file(project_id: str, file_id: str, expected_revision: int) -> list[dict[str, Any]]:
        """Delete the current file metadata and its original and preview objects atomically."""
        return run(lambda session: delete_file_content(session, project_id, file_id, expected_revision, preview_only=False))

    @server.tool()
    def arteligo_delete_preview(project_id: str, file_id: str, expected_revision: int) -> list[dict[str, Any]]:
        """Remove the current preview and its object without deleting the original file."""
        return run(lambda session: delete_file_content(session, project_id, file_id, expected_revision, preview_only=True))


    @server.tool()
    def arteligo_upload_file(
        project_id: str,
        source: str,
        parent_folder_id: str | None = None,
        upload_id: str | None = None,
    ) -> dict[str, Any]:
        """Encrypt a local file and upload ciphertext directly; pass a pending upload ID to resume."""
        return run(
            lambda session: upload_file(
                session,
                project_id=project_id,
                source=files.input_name(source),
                source_opener=lambda: files.input(source),
                parent_folder_id=parent_folder_id,
                upload_id=upload_id,
            )
        )

    @server.tool()
    def arteligo_upload_wav_preview(
        project_id: str, file_id: str, source: str
    ) -> dict[str, str]:
        """Verify an allowed input WAV, encode it with trusted local tools, and publish its preview."""
        with files.input(source) as stream:
            return run(
                lambda session: upload_wav_preview(
                    session, project_id=project_id, file_id=file_id,
                    source=files.input_name(source), source_stream=stream,
                )
            )

    @server.tool()
    def arteligo_download_file(
        project_id: str, file_id: str, destination: str
    ) -> dict[str, int]:
        """Authenticate a file and publish a new exclusive path under the granted output directory."""
        with files.output(destination) as output:
            written = run(
                lambda session: _download_to_stream(
                    session, project_id=project_id, file_id=file_id,
                    output=output.stream,
                )
            )
            if isinstance(written, CallToolResult):
                return written
            output.publish()
            return {"bytes_written": written}

    register_conversation_tools(server, run)
    return server
