"""Generate public SDK clients from the product-owned canonical OpenAPI."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CLIENT_PACKAGES = {
    "arteligo": "arteligo_public_api_client",
    "account": "account_public_api_client",
}


def generate(contract: Path, output: Path, *, operation_wrappers: bool) -> None:
    environment = {
        name: os.environ[name]
        for name in (
            "PATH",
            "HOME",
            "LANG",
            "LC_ALL",
            "TMPDIR",
            "UV_CACHE_DIR",
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "NO_PROXY",
            "http_proxy",
            "https_proxy",
            "no_proxy",
            "SSL_CERT_FILE",
            "SSL_CERT_DIR",
            "REQUESTS_CA_BUNDLE",
        )
        if name in os.environ
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f".{output.name}-", dir=output.parent
    ) as temporary:
        staged = Path(temporary) / output.name
        subprocess.run(
            [
                "uvx",
                "--from",
                "openapi-python-client==0.28.0",
                "--with",
                "ruff==0.16.9",
                "openapi-python-client",
                "generate",
                "--path",
                str(contract),
                "--meta",
                "none",
                "--output-path",
                str(staged),
                "--config",
                str(ROOT / "tool" / "public-contract-config.json"),
            ],
            cwd=ROOT,
            env=environment,
            check=True,
        )
        if operation_wrappers:
            emit_operations(contract, staged)
        previous = Path(temporary) / "previous"
        if output.exists():
            output.rename(previous)
        try:
            staged.rename(output)
        except BaseException:
            if previous.exists():
                previous.rename(output)
            raise
        if previous.exists():
            shutil.rmtree(previous)


def route_identity(method: str, path: str) -> tuple[str, str]:
    # Generated Python identifiers normalize canonical path parameter spelling.
    return method.lower(), re.sub(r"\{[^{}]+\}", "{}", path)


def route_string(value: ast.expr) -> str:
    match value:
        case ast.Constant(value=str(literal)):
            return literal
        case ast.JoinedStr(values=parts):
            result = []
            for part in parts:
                match part:
                    case ast.Constant(value=str(literal)):
                        result.append(literal)
                    case ast.FormattedValue(value=expression):
                        result.append("{" + ast.unparse(expression) + "}")
                    case _:
                        raise ValueError("Unsupported generated route string component")
            return "".join(result)
        case ast.Call(
            func=ast.Attribute(value=ast.Constant(value=str(literal)), attr="format")
        ):
            return literal
        case _:
            raise ValueError("Unsupported generated route string expression")


def emit_operations(contract: Path, output: Path) -> None:
    """Bind canonical operation IDs to the actual generated typed endpoints."""
    document = yaml.safe_load(contract.read_text())
    operations = {
        route_identity(method, path): operation["operationId"]
        for path, item in document["paths"].items()
        for method, operation in item.items()
        if isinstance(operation, dict) and "operationId" in operation
    }
    expected_count = sum(
        1
        for item in document["paths"].values()
        for operation in item.values()
        if isinstance(operation, dict) and "operationId" in operation
    )
    if len(operations) != expected_count:
        raise ValueError("Canonical routes collide after path parameter normalization")
    imports = ["from .types import File"]
    entries = []
    for index, path in enumerate(sorted((output / "api").glob("*/*.py"))):
        tree = ast.parse(path.read_text())
        kwargs = next(
            (
                node
                for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name == "_get_kwargs"
            ),
            None,
        )
        if kwargs is None:
            continue
        route = next(
            (
                node.value
                for node in ast.walk(kwargs)
                if isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == "_kwargs"
                and isinstance(node.value, ast.Dict)
            ),
            None,
        )
        if route is None:
            continue
        literals: dict[str, str] = {}
        for key, value in zip(route.keys, route.values, strict=True):
            match key:
                case ast.Constant(value=str(name)) if name in {"method", "url"}:
                    literals[name] = route_string(value)
        operation = operations[route_identity(literals["method"], literals["url"])]
        alias = f"_endpoint_{index}"
        imports.append(f"from .api.{path.parent.name} import {path.stem} as {alias}")
        conversions = []
        for argument in kwargs.args.args + kwargs.args.kwonlyargs:
            if argument.annotation is None:
                continue
            names = [
                node.id
                for node in ast.walk(argument.annotation)
                if isinstance(node, ast.Name)
            ]
            model = next(
                (
                    name
                    for name in names
                    if name
                    not in {
                        "str",
                        "int",
                        "bool",
                        "float",
                        "list",
                        "dict",
                        "Any",
                        "Unset",
                    }
                ),
                None,
            )
            if model is not None:
                if argument.arg == "body":
                    conversion = (
                        "File(payload=body)"
                        if model == "File"
                        else f"{alias}.{model}.from_dict(body)"
                    )
                    conversions.append(f"    parameters['body'] = {conversion}")
                else:
                    conversions.append(
                        f"    if {argument.arg!r} in parameters:\n"
                        f"        parameters[{argument.arg!r}] = {alias}.{model}(parameters[{argument.arg!r}])"
                    )
        name = f"_call_{index}"
        entries.append((operation, name, alias))
        imports.extend(
            [
                "",
                f"def {name}(client, body=None, **parameters):",
                *conversions,
                f"    return {alias}.sync_detailed(client=client, **parameters)",
            ]
        )
    imports.extend(
        [
            "",
            "OPERATIONS = {",
            *[
                f"    {json.dumps(operation)}: {name},"
                for operation, name, _ in entries
            ],
            "}",
            "",
            "STREAM_OPERATIONS = {",
            *[
                f"    {json.dumps(operation)}: {alias}._get_kwargs,"
                for operation, _, alias in entries
                if any(
                    item.get("operationId") == operation
                    and "application/x-ndjson"
                    in item.get("requestBody", {}).get("content", {})
                    for paths in document["paths"].values()
                    for item in paths.values()
                    if isinstance(item, dict)
                )
            ],
            "}",
            "",
        ]
    )
    (output / "operations.py").write_text("\n".join(imports))
    emitted = {operation for operation, _, _ in entries}
    if emitted != set(operations.values()) or len(entries) != len(emitted):
        raise ValueError(
            "Generated endpoints do not exactly cover canonical operation IDs"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("generate", "check"))
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--product", choices=CLIENT_PACKAGES, default="arteligo")
    args = parser.parse_args()
    contract = args.contract.resolve(strict=True)
    output = ROOT / "generated" / CLIENT_PACKAGES[args.product]
    if args.action == "generate":
        generate(contract, output, operation_wrappers=args.product == "account")
        return
    with tempfile.TemporaryDirectory(prefix="public-contract-") as temporary:
        staged = Path(temporary) / output.name
        generate(contract, staged, operation_wrappers=args.product == "account")

        def sources(directory: Path) -> dict[str, bytes]:
            return {
                path.relative_to(directory).as_posix(): path.read_bytes()
                for path in directory.rglob("*")
                if path.is_file() and "__pycache__" not in path.parts
            }

        expected, actual = sources(staged), sources(output)
        differences = [
            name
            for name in sorted(expected.keys() | actual.keys())
            if expected.get(name) != actual.get(name)
        ]
        if differences:
            raise SystemExit(
                "Generated Python client drift:\n" + "\n".join(differences)
            )


if __name__ == "__main__":
    main()
