"""Generate public SDK clients from the product-owned canonical OpenAPI."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CLIENT_PACKAGES = {
    "arteligo": "arteligo_public_api_client",
    "account": "account_public_api_client",
}


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
         "--output-path", str(output), "--overwrite",
         "--config", str(ROOT / "tool" / "public-contract-config.json")],
        cwd=ROOT, env=environment, check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("generate",))
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--product", choices=CLIENT_PACKAGES, default="arteligo")
    args = parser.parse_args()
    contract = args.contract.resolve(strict=True)
    generate(contract, ROOT / "generated" / CLIENT_PACKAGES[args.product])


if __name__ == "__main__":
    main()
