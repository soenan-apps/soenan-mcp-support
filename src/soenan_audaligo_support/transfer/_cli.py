from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ._http import TransferError
from ._workflow import download_file, download_preview, upload_file

_MAXIMUM_HANDOFF_BYTES = 256 * 1024


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    arguments = parser.parse_args(argv)
    try:
        structured_content = _read_handoff()
        if arguments.command == "upload":
            result: Any = upload_file(
                structured_content,
                source=Path(arguments.source),
            )
        elif arguments.command == "download":
            result = {
                "writtenBytes": download_file(
                    structured_content,
                    destination=Path(arguments.destination),
                )
            }
        else:
            result = {
                "writtenBytes": download_preview(
                    structured_content,
                    destination=Path(arguments.destination),
                )
            }
        print(json.dumps(result, separators=(",", ":"), sort_keys=True))
        return 0
    except OSError:
        error = TransferError("local file operation failed", code="local_io_failed")
    except (TransferError, TypeError, ValueError) as caught:
        error = (
            caught
            if isinstance(caught, TransferError)
            else TransferError("transfer input is invalid", code="input_invalid")
        )
    print(json.dumps(error.wire_value(), separators=(",", ":")), file=sys.stderr)
    return 1


def _read_handoff() -> dict[str, Any]:
    raw = sys.stdin.buffer.read(_MAXIMUM_HANDOFF_BYTES + 1)
    if not raw or len(raw) > _MAXIMUM_HANDOFF_BYTES:
        raise TransferError(
            "structuredContent stdin is invalid", code="handoff_invalid"
        )
    try:
        value = json.loads(raw, object_pairs_hook=_strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise TransferError(
            "structuredContent stdin is invalid", code="handoff_invalid"
        ) from None
    if not isinstance(value, dict):
        raise TransferError(
            "structuredContent stdin must be an object", code="handoff_invalid"
        )
    return value


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON field")
        value[key] = item
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="soenan-audaligo-transfer",
        description="Consume an MCP handoff and transfer encrypted Audaligo content.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    upload = commands.add_parser("upload", help="upload one authorized local file")
    upload.add_argument("--source", required=True)

    download = commands.add_parser("download", help="download one authorized file")
    download.add_argument("--destination", required=True)

    preview = commands.add_parser(
        "download-preview", help="download one authorized encrypted preview"
    )
    preview.add_argument("--destination", required=True)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
