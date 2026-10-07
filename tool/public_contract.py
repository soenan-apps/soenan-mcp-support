"""Generate or check the public SDK client from Arteligo's canonical OpenAPI."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated/arteligo_public_api_client"


def generate(contract: Path, output: Path) -> None:
    environment = {
        name: os.environ[name]
        for name in (
            "PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "UV_CACHE_DIR",
            "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy",
            "no_proxy", "SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE",
        )
        if name in os.environ
    }
    subprocess.run(
        ["uvx", "--from", "openapi-python-client==0.28.0", "--with", "ruff==0.16.9",
         "openapi-python-client", "generate", "--path", str(contract), "--meta", "none",
         "--output-path", str(output), "--overwrite"],
        cwd=ROOT, env=environment, check=True,
    )


def files(directory: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(directory)): path.read_bytes()
        for path in directory.rglob("*")
        if path.is_file() and not {"__pycache__", ".ruff_cache"}.intersection(path.parts)
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("generate", "check"))
    parser.add_argument("--contract", required=True, type=Path)
    args = parser.parse_args()
    contract = args.contract.resolve(strict=True)
    if args.action == "generate":
        generate(contract, GENERATED)
        return
    with tempfile.TemporaryDirectory(prefix="arteligo-sdk-contract-") as directory:
        output = Path(directory) / GENERATED.name
        generate(contract, output)
        expected, actual = files(output), files(GENERATED)
        changed = sorted(name for name in expected.keys() | actual.keys()
                         if expected.get(name) != actual.get(name))
        if changed:
            raise SystemExit("Generated SDK client differs: " + ", ".join(changed[:10]))
    print("Arteligo SDK public client matches the canonical contract")


if __name__ == "__main__":
    main()
