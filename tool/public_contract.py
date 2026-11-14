"""Generate SDK clients with the Account-owned public contract generator."""

from __future__ import annotations

import argparse
import importlib.util
import tempfile
from importlib.machinery import ModuleSpec, SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("generate", "check"))
    parser.add_argument("--contract", required=True, type=Path)
    args = parser.parse_args()
    source = ROOT.parent / "soenan-account/scripts/account-public-python-codegen.py"
    loader = SourceFileLoader("account_public_codegen", str(source))
    spec = ModuleSpec(loader.name, loader, origin=str(source))
    spec.has_location = True
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    output = ROOT / "generated/arteligo_public_api_client"
    if args.action == "generate":
        module.generate(
            args.contract.resolve(strict=True), output, operation_wrappers=False
        )
        return
    with tempfile.TemporaryDirectory(prefix="public-contract-") as temporary:
        staged = Path(temporary) / output.name
        module.generate(
            args.contract.resolve(strict=True), staged, operation_wrappers=False
        )

        def sources(directory: Path) -> dict[str, bytes]:
            return {
                path.relative_to(directory).as_posix(): path.read_bytes()
                for path in directory.rglob("*")
                if path.is_file() and "__pycache__" not in path.parts
            }

        if sources(staged) != sources(output):
            raise SystemExit("Generated Python client drift")


if __name__ == "__main__":
    main()
