from __future__ import annotations

from collections.abc import Callable
from contextlib import asynccontextmanager
from functools import partial
from typing import Any, Literal

import anyio
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.fastmcp.tools.base import Tool
from mcp.types import CallToolResult, Tool as MCPTool
from pydantic import ValidationError

from ..transfer import TransferError, upload_file, upload_wav_preview
from ..transfer._workflow import _download_to_stream
from ._crypto import E2eeError
from ._directory import EncryptedDirectory
from ._file_boundary import FileBoundary
from ._local_broker import LocalBrokerClient, LocalGrantHandle, MemoryGrant
from ._mcp_conversations import register_conversation_tools
from ._records import EncryptedRecords
from ._session import DeviceSession


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
            converted = tool.fn_metadata.convert_result(result)
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


def _broker_operations(
    session: DeviceSession, grant: MemoryGrant, files: FileBoundary
) -> _OperationRegistry:
    server = _OperationRegistry(grant)

    def run(operation: Callable[[DeviceSession], Any]) -> Any:
        try:
            session.refresh()
            session.require_approved()
            return operation(session)
        except E2eeError as error:
            raise ToolError(error.code) from None
        except TransferError as error:
            raise ToolError(error.code) from None
        except (KeyError, TypeError, ValueError, OSError):
            raise ToolError("invalid_content_or_transport") from None

    @server.tool()
    def arteligo_list_projects() -> dict[str, Any]:
        """List only the explicitly granted projects using their current account authorization."""
        result = run(lambda session: session.call("e2eeListProjects"))
        return {
            "projects": [
                project for project in result["projects"]
                if project["project_id"] in grant.projects
            ]
        }

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
            "file",
            "preview",
            "submission",
            "comment",
            "chat",
            "stage",
            "schedule",
        ],
        expected_revision: int,
        key_epoch: int,
        value: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Encrypt and sign a record update; a revision conflict requires rereading the current record."""
        if kind in {"chat", "comment"}:
            raise ToolError("conversation_operation_required")
        return run(
            lambda session: EncryptedRecords(session).write(
                project_id,
                key_epoch=key_epoch,
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
        kind: Literal["project", "directory", "file", "preview", "submission", "stage", "schedule"],
        expected_revision: int,
        key_epoch: int,
    ) -> list[dict[str, Any]]:
        """Sign a metadata-only deletion marker; no document is encrypted or retained in the marker."""
        return run(
            lambda session: EncryptedRecords(session).write(
                project_id,
                key_epoch=key_epoch,
                records=[{
                    "record_id": record_id,
                    "kind": kind,
                    "expected_revision": expected_revision,
                    "deleted": True,
                }],
            )
        )


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
            output.publish()
            return {"bytes_written": written}

    register_conversation_tools(server, run)
    return server
