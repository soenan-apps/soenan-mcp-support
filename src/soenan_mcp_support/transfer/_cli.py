from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from ._http import TransferError
from ._mcp import MCPHTTPToolCaller
from ._workflow import download_file, upload_file


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    arguments = parser.parse_args(argv)
    endpoint = arguments.mcp_url or os.environ.get("SOENAN_MCP_URL")
    access_token = os.environ.get(arguments.access_token_env)
    if not endpoint:
        parser.error("set --mcp-url or SOENAN_MCP_URL")
    if not access_token:
        parser.error(f"set the access token in {arguments.access_token_env}")

    try:
        caller = MCPHTTPToolCaller(endpoint=endpoint, access_token=access_token)
        if arguments.command == "upload":
            source = Path(arguments.source)
            result = upload_file(
                caller,
                project_id=arguments.project_id,
                filename=arguments.filename or source.name,
                source=source,
                operation_id=arguments.operation_id,
                mix_version_id=arguments.mix_version_id,
            )
            print(json.dumps(result, separators=(",", ":"), ensure_ascii=True))
        else:
            written = download_file(
                caller,
                project_id=arguments.project_id,
                file_id=arguments.file_id,
                destination=Path(arguments.destination),
            )
            print(json.dumps({"writtenBytes": written}, separators=(",", ":")))
        return 0
    except (TransferError, OSError, ValueError) as error:
        print(f"soenan-mcp-transfer: {error}", file=sys.stderr)
        return 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="soenan-mcp-transfer",
        description=(
            "Encrypt or decrypt Audaligo files locally while transferring ciphertext "
            "directly with Railway Bucket capabilities."
        ),
    )
    parser.add_argument(
        "--mcp-url",
        help="Soenan MCP resource URL; defaults to SOENAN_MCP_URL",
    )
    parser.add_argument(
        "--access-token-env",
        default="SOENAN_MCP_ACCESS_TOKEN",
        help=(
            "environment variable containing the OAuth bearer token "
            "(default: SOENAN_MCP_ACCESS_TOKEN)"
        ),
    )
    commands = parser.add_subparsers(dest="command", required=True)

    upload = commands.add_parser("upload", help="encrypt and upload one local file")
    upload.add_argument("--project-id", required=True)
    upload.add_argument("--source", required=True)
    upload.add_argument("--operation-id", required=True)
    upload.add_argument("--filename")
    upload.add_argument("--mix-version-id")

    download = commands.add_parser("download", help="download and decrypt one file")
    download.add_argument("--project-id", required=True)
    download.add_argument("--file-id", required=True)
    download.add_argument("--destination", required=True)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
