from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from ..transfer import TransferError, download_file, upload_file, upload_wav_preview
from ._crypto import E2eeError
from ._directory import EncryptedDirectory
from ._directory_migration import abort_directory_migration, migrate_directory
from ._mcp_conversations import register_conversation_tools
from ._records import EncryptedRecords
from ._session import DeviceSession


def create_local_mcp(session_factory: Callable[[], DeviceSession]) -> FastMCP:
    server = FastMCP(
        "Arteligo trusted local client",
        instructions=(
            "Arteligo content is decrypted and encrypted on this computer using its approved device. "
            "Keys, recovery codes, and OAuth tokens are never exposed by these tools. "
            "Device approval and recovery require the human-operated arteligo CLI."
        ),
    )

    def run(operation: Callable[[DeviceSession], Any]) -> Any:
        session = None
        try:
            session = session_factory()
            session.require_approved()
            return operation(session)
        except E2eeError as error:
            raise ToolError(error.code) from None
        except TransferError as error:
            raise ToolError(error.code) from None
        except (KeyError, TypeError, ValueError, OSError):
            raise ToolError("invalid_content_or_transport") from None
        finally:
            if session is not None:
                session.lock()

    @server.tool()
    def arteligo_list_projects() -> dict[str, Any]:
        """List project IDs, authorization, and key epochs available to this account."""
        return run(lambda session: session.api.call("e2eeListProjects"))

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
        """Read and decrypt up to 256 selected opaque record IDs without reading the project."""
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
    def arteligo_migrate_directory(
        project_id: str, maximum_batches: int = 64
    ) -> dict[str, Any]:
        """Advance or resume the encrypted folder migration, preserving existing file and object IDs."""
        return run(
            lambda session: migrate_directory(
                EncryptedRecords(session), project_id, maximum_batches=maximum_batches
            )
        )

    @server.tool()
    def arteligo_abort_directory_migration(
        project_id: str, maximum_batches: int = 64
    ) -> dict[str, Any]:
        """Discard unpublished migration nodes in bounded batches, retaining the original directory."""
        return run(
            lambda session: abort_directory_migration(
                EncryptedRecords(session), project_id, maximum_batches=maximum_batches
            )
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
        deleted: bool = False,
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
                        "deleted": deleted,
                    }
                ],
            )
        )

    @server.tool()
    def arteligo_create_project(
        value: dict[str, Any],
        owner_org: str,
        participation_policy: Literal["private", "organization"] = "private",
    ) -> dict[str, str]:
        """Create a project with locally encrypted content and separately wrapped project keys."""
        return run(
            lambda session: {
                "project_id": EncryptedRecords(session).create_project(
                    value=value,
                    owner_org=owner_org,
                    participation_policy=participation_policy,
                )
            }
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
                source=source,
                parent_folder_id=parent_folder_id,
                upload_id=upload_id,
            )
        )

    @server.tool()
    def arteligo_upload_wav_preview(
        project_id: str, file_id: str, source: str
    ) -> dict[str, str]:
        """Verify a local WAV against the uploaded source, encode Opus locally, and publish its encrypted preview."""
        return run(
            lambda session: upload_wav_preview(
                session, project_id=project_id, file_id=file_id, source=source
            )
        )

    @server.tool()
    def arteligo_download_file(
        project_id: str, file_id: str, destination: str
    ) -> dict[str, int]:
        """Authenticate and decrypt a file to a new local path; existing files are never overwritten."""
        return run(
            lambda session: {
                "bytes_written": download_file(
                    session,
                    project_id=project_id,
                    file_id=file_id,
                    destination=destination,
                )
            }
        )

    register_conversation_tools(server, run)
    return server
