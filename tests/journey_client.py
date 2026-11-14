"""Process entry for browser journeys using the installed SDK and MCP client."""

from __future__ import annotations

import asyncio
import base64
import faulthandler
import json
import os
import pty
import selectors
import signal
import subprocess
import sys
from contextlib import AsyncExitStack
from dataclasses import asdict
from pathlib import Path
from traceback import walk_tb


def public(value):
    from soenan_arteligo_support.e2ee import AcceptedCommand
    from soenan_arteligo_support.e2ee._mcp import _public_result

    if isinstance(value, AcceptedCommand):
        raise RuntimeError("accepted_command_requires_finalization")
    return _public_result(value)


def failure(error):
    frames = [
        f"{Path(frame.f_code.co_filename).name}:{line}:{frame.f_code.co_name}"
        for frame, line in walk_tb(error.__traceback__)
    ]
    diagnostic = f"{type(error).__name__} at {' -> '.join(frames)}"
    import httpx

    if isinstance(error, httpx.HTTPStatusError):
        diagnostic += f" HTTP {error.response.status_code}"
        try:
            envelope = error.response.json()
        except ValueError, httpx.ResponseNotRead:
            envelope = None
        if isinstance(envelope, dict) and isinstance(envelope.get("error"), dict):
            rpc_error = envelope["error"]
            if isinstance(rpc_error.get("code"), int):
                diagnostic += f" JSON-RPC {rpc_error['code']}"
            data = rpc_error.get("data")
            if isinstance(data, dict) and data.get("outcome") in {
                "delivery_pending",
                "source_behind",
            }:
                diagnostic += f" outcome={data['outcome']}"
    if isinstance(error, BaseExceptionGroup):
        leaves = list(error.exceptions)
        while any(isinstance(child, BaseExceptionGroup) for child in leaves):
            leaves = [
                leaf
                for child in leaves
                for leaf in (
                    child.exceptions
                    if isinstance(child, BaseExceptionGroup)
                    else [child]
                )
            ]
        if all(
            isinstance(child, httpx.HTTPStatusError)
            and child.response.status_code == 401
            for child in leaves
        ):
            return {
                "error": 401,
                "diagnostic": diagnostic
                + " ["
                + "; ".join(failure(child)["diagnostic"] for child in leaves)
                + "]",
            }
        diagnostic += (
            " ["
            + "; ".join(failure(child)["diagnostic"] for child in error.exceptions)
            + "]"
        )
    elif error.__cause__ is not None:
        diagnostic += " caused by " + failure(error.__cause__)["diagnostic"]
    elif error.__context__ is not None:
        diagnostic += " during " + failure(error.__context__)["diagnostic"]
    return {
        "error": getattr(error, "code", type(error).__name__),
        "diagnostic": diagnostic,
    }


def sdk(request, session, records):
    from google.protobuf.json_format import ParseDict
    from google.protobuf.timestamp_pb2 import Timestamp
    from soenan.arteligo.application.v1 import application_pb2 as app
    from soenan.arteligo.domain.v1 import domain_pb2 as domain

    from soenan_arteligo_support.e2ee import (
        EncryptedConversations,
        EncryptedDirectory,
        approve_invitation,
        create_invitation,
        request_invitation,
        revoke_invitation,
    )
    from soenan_arteligo_support.transfer import (
        download_file,
        upload_file,
        upload_wav_preview,
    )

    target = request["target"]
    method = request["method"]
    arguments = request.get("arguments", {})
    positional = request.get("positional", [])
    if target == "metadata" and method == "read":
        record = records.read(request["project"], [arguments["file_id"]])[
            arguments["file_id"]
        ]
        return public(record["value"])
    if target == "relay":
        from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto

        project = request["project"]
        if method == "prepare":
            key = session.project(project).protection_key
            identifier = arguments["record_id"]
            operation_id = arguments["operation_id"]
            command = session.prepare(
                project,
                operation_id=operation_id,
                values=[
                    crypto.ValueMutation(
                        id=identifier,
                        expected_revision=0,
                        protection_key=key,
                        plaintext=records._payload(
                            ParseDict(arguments["value"], domain.RecordContent()),
                            "stage",
                        ),
                        kind="stage",
                        incarnation=operation_id,
                    )
                ],
                binding=app.RecordMutationBinding(
                    heads=[
                        app.RecordHead(
                            id=identifier,
                            revision=1,
                            kind="stage",
                            incarnation=operation_id,
                            content=app.RecordContentHead(),
                            author_device_id=session.device_id,
                        )
                    ]
                ).SerializeToString(),
            )
            message = app.CommitCryptoRequest(
                project_id=project,
                command=command,
                signer_public_key=session.signing_public_key,
            )
            return {
                "path": "/api/e2ee/crypto/commit",
                "body": {
                    "bytes": base64.b64encode(message.SerializeToString()).decode()
                },
            }
        if method == "read_request":
            message = app.ReadCryptoRequest(
                project_id=project,
                device_id=session.device_id,
                view="by_ids",
                value_ids=arguments["record_ids"],
            )
            return {
                "path": "/api/e2ee/crypto/read",
                "body": {
                    "bytes": base64.b64encode(message.SerializeToString()).decode()
                },
            }
        if method == "open_read":
            response = app.ReadCryptoResponse.FromString(
                base64.b64decode(arguments["bytes"], validate=True)
            )
            return public(
                [records._record(item) for item in session.open_bundle(response.bundle)]
            )
        raise ValueError("unsupported_relay_operation")
    if target == "identity":
        from soenan.account.identity.v1 import identity_pb2 as identity

        if method == "evidence":
            from journey_identity_evidence import public_identity_evidence

            return public_identity_evidence(session.identity, arguments)
        if method not in {
            "pairing_request",
            "accept_approval",
            "synchronize",
            "state",
            "device_id",
            "subject",
        }:
            raise ValueError("unsupported_identity_operation")
        if method == "accept_approval":
            positional[0] = ParseDict(positional[0], identity.IdentityChangeResponse())
        operation = getattr(session.identity, method)
        return public(
            operation(*positional, **arguments) if callable(operation) else operation
        )
    if target == "session":
        if method == "catalog_response":
            response = session.catalog_response(*positional, **arguments)
            response.ClearField("bundle")
            return public(response)
        allowed = {"state", "device_id", "subject"}
        if method not in allowed:
            raise ValueError("unsupported_session_operation")
        operation = getattr(session, method)
        return public(
            operation(*positional, **arguments) if callable(operation) else operation
        )
    if target == "records":
        if method not in {
            "create_project",
            "read",
            "read_many",
            "current",
            "changes",
            "write",
            "history",
            "resume_write",
        }:
            raise ValueError("unsupported_record_operation")
        if method == "create_project":
            arguments["value"] = ParseDict(arguments["value"], domain.ProjectInfo())
        elif method == "write":
            for draft in arguments["records"]:
                if "value" in draft:
                    draft["value"] = ParseDict(draft["value"], domain.RecordContent())
            if "preconditions" in arguments:
                arguments["preconditions"] = [
                    ParseDict(condition, app.RecordPrecondition())
                    for condition in arguments["preconditions"]
                ]
        return public(getattr(records, method)(*positional, **arguments))
    if target == "directory":
        if method not in {"page", "insert"}:
            raise ValueError("unsupported_directory_operation")
        if method == "insert":
            positional[0] = ParseDict(positional[0], domain.ProjectEntry())
            for draft in arguments.get("additional_records", []):
                if "value" in draft:
                    draft["value"] = ParseDict(draft["value"], domain.RecordContent())
        elif method == "page" and arguments.get("cursor") is not None:
            cursor = arguments["cursor"]
            arguments["cursor"] = {
                **cursor,
                "last": ParseDict(cursor["last"], domain.OrderedEntryKey()),
            }
        return public(
            getattr(EncryptedDirectory(records, request["project"]), method)(
                *positional, **arguments
            )
        )
    if target == "conversation":
        if method not in {
            "chat_messages",
            "chat_events",
            "chat_message",
            "chat_message_history",
            "write_chat",
            "comment_threads",
            "comment_thread",
            "comment_replies",
            "comment_reply",
            "create_comment",
            "create_reply",
            "edit_comment",
            "edit_reply",
            "set_resolution",
        }:
            raise ValueError("unsupported_conversation_operation")
        for name in ("created_at", "committed_at"):
            if name in arguments:
                arguments[name] = ParseDict(arguments[name], Timestamp())
        for name in ("author", "actor"):
            if name in arguments:
                arguments[name] = ParseDict(arguments[name], domain.MemberActor())
        if "anchor" in arguments:
            arguments["anchor"] = ParseDict(arguments["anchor"], domain.ReviewAnchor())
        if (
            method in {"comment_threads", "comment_replies"}
            and arguments.get("after") is not None
        ):
            arguments["after"] = ParseDict(arguments["after"], domain.CommentCursor())
        if "references" in arguments:
            arguments["references"] = [
                ParseDict(value, domain.ProjectReference())
                for value in arguments["references"]
            ]
        return public(
            getattr(EncryptedConversations(records, request["project"]), method)(
                *positional, **arguments
            )
        )
    operations = {
        "create_invitation": create_invitation,
        "request_invitation": request_invitation,
        "approve_invitation": approve_invitation,
        "revoke_invitation": revoke_invitation,
        "upload_file": upload_file,
        "download_file": download_file,
        "upload_wav_preview": upload_wav_preview,
    }
    if target != "operation" or method not in operations:
        raise ValueError("unsupported_sdk_operation")
    return public(operations[method](session, *positional, **arguments))


def sdk_process():
    faulthandler.enable()
    faulthandler.register(signal.SIGTERM, chain=True)
    from journey_response_loss import ProbeRequest, ResponseLossProbe

    from soenan_arteligo_support.e2ee import (
        EncryptedRecords,
        FileProfileStore,
        open_session,
    )

    configuration = json.loads(sys.stdin.readline())
    probe = None
    if "state_directory" in configuration:
        configuration["session"]["store"] = FileProfileStore(
            configuration["state_directory"], configuration["session"]["profile"]
        )
        probe = ResponseLossProbe(
            directory=configuration["state_directory"],
            profile=configuration["session"]["profile"],
            account_origin=configuration["session"]["account_origin"],
            arteligo_origin=configuration["session"]["arteligo_origin"],
        )
        probe.install()
    session = None
    records = None
    opening_error = None
    try:
        try:
            session = open_session(**configuration["session"])
            records = EncryptedRecords(session)
            print(
                json.dumps({"result": {"state": "open", "process_id": os.getpid()}}),
                flush=True,
            )
        except Exception as error:
            opening_error = error
            print(json.dumps(failure(error)), flush=True)
        for line in sys.stdin:
            try:
                request = json.loads(line)
                if request["target"] == "response_loss":
                    if probe is None:
                        raise ValueError("response_loss_requires_state_directory")
                    result = asdict(probe.dispatch(ProbeRequest.parse(request)))
                elif opening_error is not None:
                    raise opening_error
                else:
                    result = sdk(request, session, records)
                print(json.dumps({"result": result}), flush=True)
            except Exception as error:
                print(json.dumps(failure(error)), flush=True)
    finally:
        if session is not None:
            session.lock()
        if probe is not None:
            probe.close()


def terminal(arguments):
    master, slave = pty.openpty()
    environment = dict(os.environ)
    environment["BROWSER"] = f"{sys.executable} {Path(__file__).resolve()} browser %s"
    child = subprocess.Popen(
        [sys.executable, "-m", "soenan_arteligo_support.e2ee._cli", *arguments],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        env=environment,
    )
    os.close(slave)
    selector = selectors.DefaultSelector()
    try:
        selector.register(master, selectors.EVENT_READ)
        selector.register(sys.stdin, selectors.EVENT_READ)
        while True:
            for key, _ in selector.select():
                if key.fileobj == master:
                    try:
                        data = os.read(master, 65536)
                    except OSError:
                        return child.wait()
                    if not data:
                        return child.wait()
                    sys.stdout.buffer.write(data)
                    sys.stdout.buffer.flush()
                else:
                    data = os.read(sys.stdin.fileno(), 65536)
                    if not data:
                        child.terminate()
                        return child.wait()
                    os.write(master, data)
    finally:
        selector.close()
        os.close(master)
        if child.poll() is None:
            child.terminate()
            child.wait()


async def mcp_process():
    import httpx
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.client.streamable_http import streamablehttp_client
    from mcp.shared.exceptions import McpError

    async with AsyncExitStack() as stack:
        session = None
        while line := await asyncio.to_thread(sys.stdin.readline):
            request = json.loads(line)
            try:
                if request["method"] == "connect":
                    if request["transport"] == "stdio":
                        command = request["command"]
                        streams = await stack.enter_async_context(
                            stdio_client(
                                StdioServerParameters(
                                    command=command[0],
                                    args=command[1:],
                                    env={
                                        key: os.environ[key]
                                        for key in ("SSL_CERT_FILE",)
                                        if key in os.environ
                                    },
                                )
                            )
                        )
                        reader, writer = streams
                    else:
                        reader, writer, _ = await stack.enter_async_context(
                            streamablehttp_client(
                                request["url"],
                                headers={"Authorization": "Bearer " + request["token"]},
                            )
                        )
                    session = await stack.enter_async_context(
                        ClientSession(reader, writer)
                    )
                    result = (await session.initialize()).model_dump(
                        mode="json", by_alias=True
                    )
                elif request["method"] in {"tools/list", "tools/call"}:
                    if session is None:
                        raise ValueError("mcp_not_connected")
                    if request["method"] == "tools/list":
                        result = (await session.list_tools()).model_dump(
                            mode="json", by_alias=True
                        )
                    else:
                        result = (
                            await session.call_tool(
                                request["name"], request.get("arguments", {})
                            )
                        ).model_dump(mode="json", by_alias=True)
                else:
                    raise ValueError("unsupported_mcp_operation")
                print(json.dumps({"result": result}), flush=True)
            except McpError as error:
                print(
                    json.dumps({**failure(error), "error": error.error.code}),
                    flush=True,
                )
            except httpx.HTTPStatusError as error:
                print(
                    json.dumps({**failure(error), "error": error.response.status_code}),
                    flush=True,
                )
            except Exception as error:
                print(json.dumps(failure(error)), flush=True)


def main():
    mode = sys.argv[1]
    if mode == "browser":
        print("JOURNEY_BROWSER_URL=" + sys.argv[2], flush=True)
        return 0
    if mode == "terminal":
        try:
            return terminal(sys.argv[2:])
        except Exception as error:
            print(json.dumps(failure(error)), file=sys.stderr, flush=True)
            return 1
    if mode not in {"mcp", "sdk"}:
        raise ValueError("unsupported_process_mode")
    try:
        if mode == "mcp":
            asyncio.run(mcp_process())
        else:
            sdk_process()
    except Exception as error:
        print(json.dumps(failure(error)), flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
