from __future__ import annotations

import argparse
import getpass
import json
import sys
from pathlib import Path

from typing_extensions import assert_never

from ._admission import AdmissionResult
from ._client import open_session
from ._crypto import E2eeError
from ._oauth import ProfileVault
from ._storage import SystemSecureStore


def _public_json(path: str) -> dict:
    raw = Path(path).read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise E2eeError("invalid_input")
    return value


def _require_terminal() -> None:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise E2eeError("interactive_terminal_required")


def _verify_owner_candidate_references(
    oauth: ProfileVault, organization: str, candidate_id: str
) -> dict[str, int | str]:
    from arteligo_public_api_client.models.e2_ee_owner_candidate_offer import (
        E2EeOwnerCandidateOffer,
    )

    from ._api import GeneratedAPI
    from ._owner_protocol import OwnerBinding, OwnerOperation

    if not organization or not candidate_id:
        raise E2eeError("invalid_input")
    response = GeneratedAPI(oauth.bind()).call(
        "e2eeGetOwnerCandidates", organization_id=organization
    )
    if not isinstance(response, dict):
        raise E2eeError("invalid_response")
    candidates = response.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise E2eeError("owner_candidate_mismatch")
    matches = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise E2eeError("invalid_owner_evidence")
        binding = OwnerBinding.parse(candidate.get("offer"))
        if (binding.operation is not OwnerOperation.OFFER
                or not isinstance(binding.body, E2EeOwnerCandidateOffer)):
            raise E2eeError("invalid_owner_evidence")
        if not binding.body.candidate_id:
            raise E2eeError("invalid_owner_evidence")
        if binding.body.candidate_id == candidate_id:
            matches.append((candidate, binding))
    if len(matches) != 1:
        raise E2eeError("owner_candidate_mismatch")
    candidate, binding = matches[0]
    if (candidate.get("state") != "qualified"
            or binding.body.organization_id != organization):
        raise E2eeError("owner_candidate_mismatch")
    admission = binding.original_admission
    return {
        "status": "passed",
        "scope": "production_issuer_reference_resolution",
        "candidate_count": 1,
        "root_generation": binding.body.recovery_generation,
        "reference_count": len(admission.certificates)
        + (admission.root_evidence_digest is not None),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Arteligo の承認済みローカル端末と E2EE MCP"
    )
    parser.add_argument("--account-origin")
    parser.add_argument("--arteligo-origin")
    parser.add_argument("--profile", default="default")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in (
        "login", "logout", "status", "setup", "enroll", "reanchor", "add-by-key",
        "replace-addition-key",
    ):
        commands.add_parser(name)
    confirm_owner = commands.add_parser(
        "confirm-owner", help="所有者から直接受け取った招待リンクで既存 project の所有者を確認します",
    )
    confirm_owner.add_argument("--project", required=True, help="確認する既存 project ID")
    confirm_owner.add_argument("--invitation-id", help="URL ではなく招待コードを入力する場合の招待 ID")
    commands.add_parser("import-owner-handoff", help="Owner 変更メールのリンクを端末内で開きます")
    commands.add_parser("resume-owner-import", help="保存済みの Owner 鍵取得を再開します")
    commands.add_parser("maintain-owner-access", help="Owner 鍵と引継ぎ候補を更新します")
    publication = commands.add_parser("resume-publication", help="保存済みの署名を変えずに送信を再開します")
    publication.add_argument("--project", required=True)
    owner_identity = commands.add_parser("owner-identity", help="別の端末で確認する公開 Owner 情報を表示します")
    owner_identity.add_argument("--organization", required=True)
    verify_owner = commands.add_parser(
        "verify-owner", help="候補の公開 issuer references を読み取り専用で確認します",
    )
    verify_owner.add_argument("--organization", required=True)
    verify_owner.add_argument("--candidate", required=True)
    owner_confirm = commands.add_parser("confirm-owner-authority", help="Owner 本人から受け取った公開鍵を確認します")
    owner_confirm.add_argument("--organization", required=True)
    owner_confirm.add_argument("--identity-json", required=True)
    mcp = commands.add_parser("mcp", help="人が許可した local broker にだけ接続します")
    mcp.add_argument("--grant", required=True, help="実行中の mcp-grant が表示した短命 handle")
    grant_command = commands.add_parser("mcp-grant", help="人が確認した範囲だけを許可する foreground broker")
    grant_command.add_argument("--project", required=True, action="append", help="明示的に許可する既存 project ID")
    grant_command.add_argument("--access", required=True, choices=("read-only", "update"))
    grant_command.add_argument("--expires-in", required=True, type=int, help="有効秒数。1〜86400")
    grant_command.add_argument("--input-dir", help="読み込み専用の入力ディレクトリー")
    grant_command.add_argument("--output-dir", help="新規ファイルだけを作る別の出力ディレクトリー")
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
    handoff = None
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
        if args.command == "import-owner-handoff":
            from ._owner_access import OwnerAccess

            _require_terminal()
            handoff = OwnerAccess.consume_link(
                getpass.getpass("Owner 変更メールのリンク: ").strip(), args.arteligo_origin,
            )
        if args.command == "mcp-grant":
            _require_terminal()
            if not 0 < args.expires_in <= 86400:
                raise E2eeError("invalid_local_grant")
        store = SystemSecureStore(args.profile)
        oauth = ProfileVault(
            account_origin=args.account_origin,
            arteligo_origin=args.arteligo_origin,
            store=store,
        )
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
        if args.command == "verify-owner":
            result = _verify_owner_candidate_references(
                oauth, args.organization, args.candidate
            )
            print(json.dumps({"owner_candidate_references": result}, separators=(",", ":")))
            return 0

        def connect(*, recover: bool = False):
            return open_session(
                account_origin=args.account_origin,
                arteligo_origin=args.arteligo_origin,
                profile=args.profile,
                store=store,
                recover=recover,
                maintain_owner_access=args.command not in {"import-owner-handoff", "resume-owner-import"},
            )

        if args.command == "mcp-grant":
            from ._file_boundary import FileBoundary
            from ._local_broker import MemoryGrant, serve_local_grant

            session = connect()
            session.require_approved()
            projects = frozenset(args.project)
            available = session.call("e2eeListProjects")["projects"]
            if not projects <= {project["project_id"] for project in available}:
                raise E2eeError("project_not_authorized")
            files = FileBoundary(args.input_dir, args.output_dir)
            try:
                print("この local MCP に許可する範囲を確認してください。")
                print(json.dumps({
                    "projects": sorted(projects), "access": args.access,
                    "expires_in_seconds": args.expires_in,
                    "input_directory": files.input_directory,
                    "output_directory": files.output_directory,
                    "file_access_supported": files.file_access_supported,
                }, ensure_ascii=False))
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
        session = connect(recover=args.command == "reanchor")
        if args.command == "status":
            print(
                json.dumps(
                    {
                        "state": session.state,
                        "device_id": session.device_id,
                        "device_approval": session.device_approval,
                        "key_acquisition_progress": session.key_acquisition_progress,
                        "recovery_replacement_pending": session.recovery_replacement_pending,
                        "owner_access_blockers": session.owner_access.blockers,
                    }
                )
            )
        elif args.command in {"setup", "replace-addition-key"}:
            _require_terminal()
            if (
                args.command == "replace-addition-key"
                and session.recovery_replacement_pending
            ):
                session.resume_recovery_replacement(
                    getpass.getpass("交換処理中の端末追加キー: ").strip()
                )
                print("端末追加キーの交換を完了しました。")
                return 0
            draft = (
                session.prepare_setup()
                if args.command == "setup"
                else session.prepare_recovery_replacement()
            )
            print("次の端末追加キーをパスワードマネージャーなどに保存してください。")
            print(draft["code"])
            if getpass.getpass("保存した端末追加キーを入力: ").strip() != draft["code"]:
                raise E2eeError("addition_key_confirmation_mismatch")
            if args.command == "setup":
                session.finish_setup(draft)
            else:
                session.replace_recovery(draft)
            draft.clear()
            print(
                "初期設定が完了しました。"
                if args.command == "setup"
                else "端末追加キーを交換しました。"
            )
        elif args.command == "enroll":
            print(json.dumps(session.enroll(), ensure_ascii=False))
        elif args.command == "reanchor":
            print(json.dumps(session.reanchor(), ensure_ascii=False))
        elif args.command == "approve":
            print(
                json.dumps(
                    session.approve(_public_json(args.pairing_json)), ensure_ascii=False
                )
            )
        elif args.command == "accept-approval":
            session.accept_approval(_public_json(args.receipt_json))
            print("端末の承認を確認しました。")
        elif args.command == "confirm-owner":
            _require_terminal()
            session.require_approved()
            print(f"所有者を確認する project: {args.project}")
            print("所有者本人から直接受け取った招待リンクだけを使ってください。")
            print("招待への参加は申し込まず、現在の役割も変更しません。")
            if input("この project の所有者を確認する場合は confirm と入力してください: ").strip() != "confirm":
                raise E2eeError("owner_confirmation_cancelled")
            result = session.confirm_project_owner(
                args.project, getpass.getpass("所有者の招待リンクまたはコード: ").strip(),
                invitation_id=args.invitation_id,
            )
            print("project の所有者を確認しました。")
            print(json.dumps(result, ensure_ascii=False))
        elif args.command in {"import-owner-handoff", "resume-owner-import"}:
            _require_terminal()
            result = session.owner_access.import_handoff(handoff)
            print("Owner の履歴鍵をこの端末に保存しました。")
            print(json.dumps(result, ensure_ascii=False))
        elif args.command == "maintain-owner-access":
            session.owner_access.maintain()
            print(json.dumps({"owner_access_blockers": session.owner_access.blockers}, ensure_ascii=False))
        elif args.command == "resume-publication":
            from ._records import EncryptedRecords

            result = EncryptedRecords(session).resume_write(args.project)
            print(json.dumps({"project_id": args.project, "record_ids": [item["record_id"] for item in result]}))
        elif args.command == "owner-identity":
            print(json.dumps(session.owner_access.public_identity(args.organization), ensure_ascii=False))
        elif args.command == "confirm-owner-authority":
            _require_terminal()
            identity = _public_json(args.identity_json)
            print(f"Owner を確認する組織: {args.organization}")
            print("Owner 本人から別の信頼できる経路で受け取ったファイルだけを使ってください。")
            fingerprint = identity["owner_authority"]["binding_digest"]
            print(f"Owner 公開鍵の署名識別子: {fingerprint}")
            if input("別の経路で照合した署名識別子を入力: ").strip() != fingerprint:
                raise E2eeError("owner_confirmation_cancelled")
            session.owner_access.confirm_authority(args.organization, identity)
            session.owner_access.maintain()
            print(json.dumps({"owner_access_blockers": session.owner_access.blockers}, ensure_ascii=False))
        elif args.command == "add-by-key":
            _require_terminal()
            result = session.add_by_key(getpass.getpass("端末追加キー: ").strip())
            match result:
                case AdmissionResult.READY:
                    print("他の端末を失効させず、この端末を追加しました。")
                case AdmissionResult.KEY_ACQUISITION_PENDING:
                    print("この端末を承認しました。一部の project の鍵取得が残っています。同じ端末追加キーで再開できます。")
                    if "trust_verification_required" in session.key_acquisition_progress["remaining"].values():
                        print("署名者の信頼確認が必要な project が残っています。所有者をまだ確認していない場合は confirm-owner --project <ID> を実行してください。")
                case _:
                    assert_never(result)
            print(json.dumps(session.key_acquisition_progress, ensure_ascii=False))
        return 0
    except E2eeError as error:
        failure = {"error": error.code}
        if session is not None and session.state == "key_acquisition_pending":
            failure["device_approval"] = session.device_approval
            failure["key_acquisition_progress"] = session.key_acquisition_progress
        if error.code == "authentication_login_uncertain":
            failure["message"] = (
                "認証コードの交換結果を確認できません。"
                "新しい認証系列が作成された可能性があり、その系列の失効は確認できません。"
            )
        if error.code == "owner_confirmation_fresh_invitation_required":
            failure["message"] = (
                "所有者の現在の端末または復旧鍵を確認できません。"
                "所有者本人に新しい招待リンクを作ってもらい、直接受け取ってから confirm-owner を再実行してください。"
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
        if handoff is not None:
            handoff.clear()
        if session is not None:
            session.lock()


if __name__ == "__main__":
    raise SystemExit(main())
