from __future__ import annotations

import argparse
import getpass
import json
import sys
from pathlib import Path

from ._client import open_session
from ._crypto import E2eeError
from ._oauth import ProfileVault
from ._storage import SystemSecureStore
from ._signed_commands import AcceptedCommand


def _public_json(path: str) -> dict:
    value = json.loads(Path(path).read_bytes())
    if not isinstance(value, dict):
        raise E2eeError("invalid_input")
    return value


def _print_result(value: object) -> None:
    if isinstance(value, AcceptedCommand):
        saved = value.result
        value = {"state": "saved", "local_result": "unavailable"}
        for name in ("organization_id", "project_id", "device_id", "object_id"):
            if name in saved:
                value[name] = saved[name]
        if "records" in saved:
            value["record_ids"] = [record["record_id"] for record in saved["records"]]
    print(json.dumps(value, ensure_ascii=False))


def _require_terminal() -> None:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise E2eeError("interactive_terminal_required")


def main() -> int:
    parser = argparse.ArgumentParser(description="Arteligo の承認済みローカル端末と E2EE MCP")
    parser.add_argument("--account-origin")
    parser.add_argument("--arteligo-origin")
    parser.add_argument("--profile", default="default")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("login", "logout", "status", "setup", "enroll", "reanchor", "add-by-key", "replace-addition-key"):
        commands.add_parser(name)
    confirm_owner = commands.add_parser("confirm-owner", help="直接受け取った招待リンクで project の所有者を確認します")
    confirm_owner.add_argument("--project", required=True)
    confirm_owner.add_argument("--invitation-id")
    create_invite = commands.add_parser("create-invitation")
    create_invite.add_argument("--project", required=True)
    create_invite.add_argument("--invitation-id", required=True)
    create_invite.add_argument("--role", required=True, choices=("viewer", "editor"))
    create_invite.add_argument("--expires-at", required=True, type=int, help="有効期限の Unix 秒")
    request_invite = commands.add_parser("request-invitation")
    request_invite.add_argument("--project", required=True)
    request_invite.add_argument("--invitation-id")
    approve_invite = commands.add_parser("approve-invitation")
    approve_invite.add_argument("--project", required=True)
    approve_invite.add_argument("--invitation-id", required=True)
    approve_invite.add_argument("--subject", required=True)
    revoke_invite = commands.add_parser("revoke-invitation")
    revoke_invite.add_argument("--project", required=True)
    revoke_invite.add_argument("--invitation-id", required=True)
    commands.add_parser("catalog", help="現在利用できる組織とプロジェクトを表示します")
    group_member = commands.add_parser("prepare-group-member", help="組織メンバーへ共有 project の鍵をまとめて配送します")
    group_member.add_argument("--organization", required=True)
    group_member.add_argument("--subject", required=True)
    remove_member = commands.add_parser(
        "remove-project-member",
        help="指定したメンバーの project アクセス権限を解除します",
    )
    remove_member.add_argument("--project", required=True)
    remove_member.add_argument("--subject", required=True)
    delivery = commands.add_parser("prepare-owner-delivery", help="現在の Owner 候補へ project の鍵を配送します")
    delivery.add_argument("--project", required=True)
    delivery.add_argument("--subject", required=True)
    revoke_device = commands.add_parser("revoke-device", help="指定した端末を失効させます")
    revoke_device.add_argument("--device-id", required=True)
    publication = commands.add_parser("resume-publication", help="保存済みの署名を変えずに送信を再開します")
    publication.add_argument("--project", required=True)
    mcp = commands.add_parser("mcp", help="人が許可した local broker にだけ接続します")
    mcp.add_argument("--grant", required=True, help="実行中の mcp-grant が表示した短命 handle")
    grant_command = commands.add_parser("mcp-grant", help="人が確認した範囲だけを許可する foreground broker")
    grant_command.add_argument("--project", required=True, action="append", help="明示的に許可する既存 project ID")
    grant_command.add_argument("--access", required=True, choices=("read-only", "update"))
    grant_command.add_argument("--expires-in", required=True, type=int, help="有効秒数。1〜86400")
    grant_command.add_argument("--input-dir", help="読み込み専用の入力ディレクトリー")
    grant_command.add_argument("--output-dir", help="新規ファイルだけを作る別の出力ディレクトリー")
    approve = commands.add_parser("approve")
    approve.add_argument("--pairing-json", required=True, help="追加端末から直接受け取った公開情報")
    accept = commands.add_parser("accept-approval")
    accept.add_argument("--receipt-json", required=True, help="承認端末から直接受け取った署名済み公開情報")
    args = parser.parse_args()
    session = None
    try:
        if args.command == "mcp":
            from ._local_broker import LocalGrantHandle
            from ._mcp import create_local_mcp

            server = create_local_mcp(LocalGrantHandle.parse(args.grant))
            try:
                server.run(transport="stdio")
            finally:
                server.close_grant()
            return 0
        if not args.account_origin or not args.arteligo_origin:
            raise E2eeError("account_and_arteligo_origins_required")
        if args.command == "mcp-grant":
            _require_terminal()
            if not 0 < args.expires_in <= 86400:
                raise E2eeError("invalid_local_grant")
        store = SystemSecureStore(args.profile)
        oauth = ProfileVault(account_origin=args.account_origin, arteligo_origin=args.arteligo_origin, store=store)
        if args.command == "login":
            oauth.login()
            print("認証できました。status で端末の状態を確認してください。")
            return 0
        if args.command == "logout":
            outcome = oauth.logout()
            if outcome.known_family_revoked:
                print("このプロファイルからサインアウトし、保存されていた認証系列を失効させました。")
            else:
                print("このプロファイルはサインアウトしています。")
            return 0
        session = open_session(
            account_origin=args.account_origin, arteligo_origin=args.arteligo_origin,
            profile=args.profile, store=store,
        )
        if args.command == "mcp-grant":
            from ._file_boundary import FileBoundary
            from ._local_broker import MemoryGrant, serve_local_grant

            session.require_approved()
            projects = frozenset(args.project)
            available = set()
            cursor = ""
            while True:
                page = session.catalog(cursor=cursor)
                available.update(project["project_id"] for project in page["projects"])
                if projects <= available or not page["has_more"]:
                    break
                if page["cursor"] == cursor:
                    raise E2eeError("invalid_response")
                cursor = page["cursor"]
            if not projects <= available:
                raise E2eeError("project_not_authorized")
            files = FileBoundary(args.input_dir, args.output_dir)
            try:
                print("この local MCP に許可する範囲を確認してください。")
                _print_result({
                    "projects": sorted(projects), "access": args.access,
                    "expires_in_seconds": args.expires_in,
                    "input_directory": files.input_directory,
                    "output_directory": files.output_directory,
                    "file_access_supported": files.file_access_supported,
                })
                print("これは端末内の tool 境界です。同じ OS ユーザーの悪意あるプログラムを隔離しません。")
                print("新しい project や権限の追加には、人が新しい許可を開始する必要があります。")
                print("復号した内容は MCP host へ渡ります。host が外部 LLM を使う場合、その提供者にも内容が送られます。")
                if input("許可する場合は authorize と入力してください: ").strip() != "authorize":
                    raise E2eeError("local_grant_not_approved")
                grant = MemoryGrant(projects, args.access, args.expires_in)

                def announce(handle):
                    print(json.dumps({
                        "worker_command": [
                            sys.executable, "-m", "soenan_arteligo_support.e2ee._cli",
                            "mcp", "--grant", handle.encode(),
                        ],
                        "expires_at": handle.expires_at,
                    }), flush=True)
                    print(
                        "この端末を開いたまま MCP host で worker_command を実行してください。"
                        "Ctrl+C、期限切れ、worker の切断で新しい操作の受付を終了します。"
                        "受付済みの処理は完了まで待ちます。確定済みの更新は取り消しません。",
                        file=sys.stderr, flush=True,
                    )

                serve_local_grant(session, grant, files, announce)
            finally:
                files.close()
            return 0
        if args.command == "status":
            _print_result({"state": session.state, "device_id": session.device_id})
        elif args.command in {"setup", "replace-addition-key"}:
            _require_terminal()
            draft = session.prepare_setup() if args.command == "setup" else session.prepare_addition_key()
            try:
                print("次の端末追加キーをパスワードマネージャーなどに保存してください。")
                print(draft["code"])
                if getpass.getpass("保存した端末追加キーを入力: ").strip() != draft["code"]:
                    raise E2eeError("addition_key_confirmation_mismatch")
                if args.command == "setup":
                    session.setup(draft)
                else:
                    session.replace_addition_key(draft)
            finally:
                draft.clear()
            print("初期設定が完了しました。" if args.command == "setup" else "端末追加キーを交換しました。")
        elif args.command == "enroll":
            _print_result(session.pairing_request())
        elif args.command == "reanchor":
            _require_terminal()
            _print_result(session.reanchor())
        elif args.command == "approve":
            _require_terminal()
            _print_result(session.approve(_public_json(args.pairing_json)))
        elif args.command == "accept-approval":
            session.accept_approval(_public_json(args.receipt_json))
            print("端末の承認を確認しました。")
        elif args.command == "add-by-key":
            _require_terminal()
            session.add_by_key(getpass.getpass("端末追加キー: ").strip())
            print("他の端末を失効させず、この端末を追加しました。")
        elif args.command == "revoke-device":
            _require_terminal()
            _print_result(session.revoke_device(args.device_id))
        elif args.command == "confirm-owner":
            from ._invitations import confirm_project_owner

            _require_terminal()
            session.require_approved()
            print(f"所有者を確認する project: {args.project}")
            print("所有者本人から直接受け取った招待リンクだけを使ってください。")
            print("招待への参加は申し込まず、現在の役割も変更しません。")
            if input("この project の所有者を確認する場合は confirm と入力してください: ").strip() != "confirm":
                raise E2eeError("owner_confirmation_cancelled")
            _print_result(confirm_project_owner(
                session, args.project, getpass.getpass("所有者の招待リンクまたはコード: ").strip(),
                invitation_id=args.invitation_id,
            ))
        elif args.command in {"create-invitation", "request-invitation", "approve-invitation", "revoke-invitation"}:
            from ._invitations import approve_invitation, create_invitation, request_invitation, revoke_invitation

            _require_terminal()
            if args.command == "create-invitation":
                _print_result(create_invitation(session, args.project, args.invitation_id, role=args.role, expires_at=args.expires_at))
            elif args.command == "request-invitation":
                _print_result(request_invitation(
                    session, args.project, getpass.getpass("直接受け取った招待リンクまたはコード: ").strip(),
                    invitation_id=args.invitation_id,
                ))
            elif args.command == "approve-invitation":
                _print_result(approve_invitation(session, args.project, args.invitation_id, args.subject))
            else:
                _print_result(revoke_invitation(session, args.project, args.invitation_id))
        elif args.command == "catalog":
            _print_result(session.catalog())
        elif args.command == "prepare-owner-delivery":
            _require_terminal()
            _print_result(session.prepare_owner_delivery(args.project, args.subject))
        elif args.command == "prepare-group-member":
            _require_terminal()
            _print_result(session.prepare_group_member(args.organization, args.subject))
        elif args.command == "remove-project-member":
            _require_terminal()
            _print_result(session.remove_project_member(args.project, args.subject))
        elif args.command == "resume-publication":
            from ._records import EncryptedRecords

            result = EncryptedRecords(session).resume_write(args.project)
            if isinstance(result, AcceptedCommand):
                _print_result(result)
            else:
                _print_result({"project_id": args.project, "record_ids": [item["record_id"] for item in result]})
        return 0
    except E2eeError as error:
        failure = {"error": error.code}
        if error.code == "authentication_login_uncertain":
            failure["message"] = (
                "認証コードの交換結果を確認できません。"
                "新しい認証系列が作成された可能性があり、その系列の失効は確認できません。"
            )
        print(json.dumps(failure), file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print('{"error":"human_operation_cancelled"}', file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError, OSError):
        print('{"error":"invalid_input_or_local_state"}', file=sys.stderr)
        return 1
    finally:
        if session is not None:
            session.lock()


if __name__ == "__main__":
    raise SystemExit(main())
