from __future__ import annotations

import argparse
import getpass
import json
import sys
from pathlib import Path

from ._client import open_session
from ._crypto import E2eeError
from ._oauth import OAuthSession
from ._storage import SystemSecureStore


def _public_json(path: str) -> dict:
    raw = Path(path).read_bytes()
    if len(raw) > 512 * 1024:
        raise E2eeError("limit_exceeded")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise E2eeError("invalid_input")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Arteligo の承認済みローカル端末と E2EE MCP"
    )
    parser.add_argument("--account-origin", required=True)
    parser.add_argument("--arteligo-origin", required=True)
    parser.add_argument("--profile", default="default")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in (
        "login",
        "logout",
        "status",
        "setup",
        "enroll",
        "recover",
        "replace-recovery",
        "mcp",
    ):
        commands.add_parser(name)
    approve = commands.add_parser("approve")
    approve.add_argument(
        "--pairing-json", required=True, help="追加端末から直接受け取った公開情報"
    )
    accept = commands.add_parser("accept-approval")
    accept.add_argument(
        "--receipt-json",
        required=True,
        help="承認端末から直接受け取った署名済み公開情報",
    )
    args = parser.parse_args()
    session = None
    try:
        store = SystemSecureStore(args.profile)
        oauth = OAuthSession(
            account_origin=args.account_origin,
            arteligo_origin=args.arteligo_origin,
            store=store,
        )
        if args.command == "login":
            oauth.login()
            print("認証できました。status で端末の状態を確認してください。")
            return 0
        if args.command == "logout":
            oauth.logout()
            print("認証情報を破棄しました。")
            return 0

        def connect():
            return open_session(
                account_origin=args.account_origin,
                arteligo_origin=args.arteligo_origin,
                profile=args.profile,
                store=store,
            )

        if args.command == "mcp":
            from ._mcp import create_local_mcp

            create_local_mcp(connect).run(transport="stdio")
            return 0
        session = connect()
        if args.command == "status":
            print(
                json.dumps(
                    {
                        "state": session.state,
                        "device_id": session.device_id,
                        "recovery_replacement_pending": session.recovery_replacement_pending,
                    }
                )
            )
        elif args.command in {"setup", "replace-recovery"}:
            if not sys.stdin.isatty() or not sys.stdout.isatty():
                raise E2eeError("interactive_terminal_required")
            if (
                args.command == "replace-recovery"
                and session.recovery_replacement_pending
            ):
                session.resume_recovery_replacement(
                    getpass.getpass("交換処理中の復旧コード: ").strip()
                )
                print("復旧コードの交換を完了しました。")
                return 0
            draft = (
                session.prepare_setup()
                if args.command == "setup"
                else session.prepare_recovery_replacement()
            )
            print("次の復旧コードをパスワードマネージャーなどに保存してください。")
            print(draft["code"])
            if getpass.getpass("保存した復旧コードを入力: ").strip() != draft["code"]:
                raise E2eeError("recovery_confirmation_mismatch")
            if args.command == "setup":
                session.finish_setup(draft)
            else:
                session.replace_recovery(draft)
            draft.clear()
            print(
                "初期設定が完了しました。"
                if args.command == "setup"
                else "復旧コードを交換しました。"
            )
        elif args.command == "enroll":
            print(json.dumps(session.enroll(), ensure_ascii=False))
        elif args.command == "approve":
            print(
                json.dumps(
                    session.approve(_public_json(args.pairing_json)), ensure_ascii=False
                )
            )
        elif args.command == "accept-approval":
            session.accept_approval(_public_json(args.receipt_json))
            print("端末の承認を確認しました。")
        elif args.command == "recover":
            if not sys.stdin.isatty():
                raise E2eeError("interactive_terminal_required")
            session.restore(getpass.getpass("復旧コード: ").strip())
            print("この端末を新しい鍵で復旧しました。")
        return 0
    except E2eeError as error:
        print(json.dumps({"error": error.code}), file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError, OSError):
        print('{"error":"invalid_input_or_local_state"}', file=sys.stderr)
        return 1
    finally:
        if session is not None:
            session.lock()


if __name__ == "__main__":
    raise SystemExit(main())
