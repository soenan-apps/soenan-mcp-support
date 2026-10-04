from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from ._crypto import E2eeError
from ._records import EncryptedRecords
from ._session import DeviceSession
from ..transfer import TransferError, download_file, upload_file, upload_wav_preview
from ..transfer._workflow import snapshot


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
    def arteligo_read_snapshot(project_id: str) -> list[dict[str, Any]]:
        """Read current decrypted project records, including names, directories, comments, and chat."""
        return run(
            lambda session: [
                item
                for item in snapshot(session, project_id).values()
                if not item["deleted"]
            ]
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

    return server
