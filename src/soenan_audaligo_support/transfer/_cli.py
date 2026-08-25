from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from ._api import AudaligoTransferAPI
from ._http import DEFAULT_TIMEOUTS, TransferError
from ._workflow import download_file, upload_file


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    arguments = parser.parse_args(argv)
    endpoint = arguments.api_url or os.environ.get("AUDALIGO_API_URL")
    access_token = os.environ.get(arguments.access_token_env)
    if not endpoint:
        parser.error("set --api-url or AUDALIGO_API_URL")
    if not access_token:
        parser.error(f"set the access token in {arguments.access_token_env}")

    try:
        with AudaligoTransferAPI(
            base_url=endpoint,
            access_token=access_token,
            timeouts=DEFAULT_TIMEOUTS,
        ) as api:
            if arguments.command == "upload":
                source = Path(arguments.source)
                result = upload_file(
                    api,
                    project_id=arguments.project_id,
                    filename=arguments.filename or source.name,
                    source=source,
                    operation_id=arguments.operation_id,
                    mix_version_id=arguments.mix_version_id,
                )
                file = result.get("file")
                file_id = file.get("fileId") if isinstance(file, dict) else None
                if not isinstance(file_id, str) or not file_id:
                    raise TransferError("Audaligo upload response omitted the file ID")
                print(json.dumps({"fileId": file_id}, separators=(",", ":")))
            else:
                written = download_file(
                    api,
                    project_id=arguments.project_id,
                    file_id=arguments.file_id,
                    destination=Path(arguments.destination),
                )
                print(json.dumps({"writtenBytes": written}, separators=(",", ":")))
        return 0
    except OSError:
        print("soenan-audaligo-transfer: local file operation failed", file=sys.stderr)
        return 1
    except (TransferError, ValueError) as error:
        print(f"soenan-audaligo-transfer: {error}", file=sys.stderr)
        return 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="soenan-audaligo-transfer",
        description=(
            "Encrypt or decrypt Audaligo files locally while transferring ciphertext "
            "directly with Railway Bucket capabilities."
        ),
    )
    parser.add_argument(
        "--api-url",
        help="Audaligo API origin; defaults to AUDALIGO_API_URL",
    )
    parser.add_argument(
        "--access-token-env",
        default="AUDALIGO_ACCESS_TOKEN",
        help=(
            "environment variable containing an Audaligo-audience OAuth bearer token "
            "(default: AUDALIGO_ACCESS_TOKEN)"
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
