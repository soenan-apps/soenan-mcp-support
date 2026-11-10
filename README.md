# Arteligo のローカル E2EE クライアント

この SDK と local MCP はユーザの承認済み端末として Arteligo の内容を暗号化・復号します。プロジェクト名、ファイル名、フォルダー構成、提出物、コメント、チャットなどは送信前に暗号化します。Arteligo と remote MCP は平文の鍵や内容を受け取りません。

Account が本人確認と OAuth を管理し、Arteligo が端末の承認状態、所属、権限、署名済み暗号文、revision、Bucket capability を管理します。暗号処理は Flutter と同じ `arteligo/native/e2ee` の Rust ライブラリーを使います。Python に別の HPKE や AES-GCM 実装はありません。

## 開発環境への導入

Python 3.10 以降と Rust toolchain が必要です。資格情報の保存には、package が依存する `keyring>=25.5` と、macOS Keychain、Windows Credential Manager、Linux Secret Service のいずれかを使います。平文ファイルへ保存する keyring backend へは切り替えません。

Linux では通常の user D-Bus と、利用可能な既定 collection を持つ Secret Service が必要です。SSH・TTY から使う場合も既存の user bus に接続し、本人の通常 keyring を先に解除します。GUI prompt を利用できない環境で別の bus・collection や平文 backend を作って代用しません。保護ストアを利用できない場合、`login` は OAuth 開始前に `secure_store_unavailable` で停止します。

端末鍵、信頼記録、再試行用の署名済み command は、暗号化した文書として端末内に保存します。OS の保護領域には固定サイズの復号鍵と確定済み文書への参照を置くため、journal が増えても Windows Credential Manager の項目容量を超えません。文書を永続化してから参照を置き換え、欠損・改ざん・保護鍵の喪失はエラーにします。保存済みの鍵を作り直したり、journal を空として扱ったりはしません。

ワークスペースのルートから、二つのローカル package を同時に導入します。

```sh
uv venv soenan-mcp-support/.venv
uv pip install --python soenan-mcp-support/.venv/bin/python ./arteligo/native/e2ee './soenan-mcp-support[dev]'
```

`dev` は型検査に使う `types-protobuf` を追加します。Ruff と ty はワークスペースの `bin/soenan check` が固定バージョンで起動します。

`arteligo-e2ee-native` のビルドは、固定した `Cargo.lock` で Rust ライブラリーを作り、実行環境用の wheel に同梱します。wheel は OS と CPU ごとに作ります。

## 端末の認証と承認

以下の `ACCOUNT_ORIGIN` と `ARTELIGO_ORIGIN` は対象環境の origin に置き換えます。HTTPS を使い、ローカル開発の loopback だけ HTTP を許可します。OAuth token は OS の保護領域へ保存します。端末の秘密鍵は OS の保護鍵で暗号化し、origin と account ごとに分離します。

```sh
arteligo --account-origin ACCOUNT_ORIGIN --arteligo-origin ARTELIGO_ORIGIN login
arteligo --account-origin ACCOUNT_ORIGIN --arteligo-origin ARTELIGO_ORIGIN status
```

`login` はブラウザーで Account の承認を開き、PKCE を使って loopback callback を受け取ります。ブラウザーへの認証情報入力はユーザが行います。CLI は固定の `arteligo-native-cli` public client と `arteligo:app` scope を使います。

同じ profile の OAuth 資格情報は、session や process ごとのコピーではなく、OS の保護領域にある一つの項目で管理します。refresh はその profile の process 間で調整し、単回利用の proof を送る前に保留状態を保存します。応答や最終保存の結果が不明な場合は、古い proof を再送しません。保護ストアが使えない場合も、平文ファイルやメモリーだけの保存へ切り替えません。

ブラウザーの操作待ちでは資格情報の lock を保持しません。同時に `login` を始めた場合は、最後に始めた操作だけが新しい資格情報を採用できます。code 交換の結果が不明なときは、以前の利用可能な資格情報を保持します。`logout` は先に古い操作を無効にし、既知の family の失効が保留中なら、それを解消するまで新しい login で上書きしません。同じ profile を古い SDK と同時に操作しないでください。旧形式の有効な access token は利用できても、refresh 可能な新形式へ自動昇格はしないため、再度 `login` が必要です。

session の置換を検出したら、その session が保持する署名・復旧・scope の鍵を利用できなくします。既に受付済みの要求まで取り消されたことにはせず、保存が確定した結果は保持します。project の読取り権限を失ったことが明示された場合は、その scope だけを回収します。一般の認証エラー、利用権の不足、見つからない応答を、project 全体の権限喪失とは扱いません。

最初の端末では `setup` を実行します。コアが端末固有の鍵、Root、受信鍵 U、端末追加キーを生成し、Account の署名と結び付けた genesis を登録します。表示された端末追加キーを安全な場所へ保存し、保存確認後に初期設定を確定します。キーを command argument、環境変数、MCP tool に渡しません。

追加端末では `add-by-key` を実行し、端末追加キーを入力します。コアは公開 Identity の署名系譜と pin、封印済み bootstrap の digest を検証してから復号し、秘密鍵から導出した公開鍵が証明と一致することを確認します。既存端末を失効させず、同じ Identity へ新端末を追加します。

QR 承認では、追加端末の `enroll` が生成した署名付き公開情報を承認済み端末へ直接渡します。既存端末で `approve --pairing-json pairing.json` を実行し、その receipt を追加端末へ戻します。追加端末の `accept-approval --receipt-json approval.json` は共通コアで受理結果と配送された鍵を検証します。SDK内部ではFlutterと同じ生成型の`SignedBytes`と`CommitCryptoResponse`を使い、CLIの入出力でJSONへ変換します。

`replace-addition-key` は新しい Root、受信鍵 U、端末追加キーを準備し、保存確認後に同じ operation として公開します。明示的な失効対象に含めていない承認済み端末は維持します。準備済み state と元の署名付き要求を保護領域へ保存し、応答が不明な場合は同じ要求で再開します。`reanchor` による通常の Root 更新でも、確認済み Identity と pin の検証を省略しません。

`catalog` は現在利用できる組織とプロジェクトを取得します。組織の現在 Owner と Owner 候補は生成型の oneof で区別し、組織の購入権限がない外部プロジェクトへの参加はプロジェクト側だけに表します。Account の所属一覧から全組織へ順に認可要求を送る処理はありません。

Python APIの`catalog_response()`は生成型の`ProjectCatalogResponse`を返します。CLIのJSON出力にはProtobufの標準表記を使い、`projectId`などを独自の別名へ変換しません。検証用の`bundle`はCLI出力から除き、local MCPでは許可したプロジェクトのentryだけを返します。

## local MCP

MCP host は、人が開始した `mcp-grant` が表示する worker の stdio command を使います。`mcp` は短命 handle がないと起動しません。

```sh
arteligo --account-origin ACCOUNT_ORIGIN --arteligo-origin ARTELIGO_ORIGIN \
  mcp-grant --project PROJECT_ID --access read-only --expires-in 3600 \
  [--input-dir INPUT_DIRECTORY] [--output-dir OUTPUT_DIRECTORY]
```

`mcp-grant` は前景で許可対象を表示し、人が `authorize` を入力した後だけ handle を発行します。対象は明示した既存 project、`read-only` または `update` の範囲、期限、任意の入出力 directory に固定し、実行中に拡大できません。worker は通常の OAuth token や端末追加キーを受け取りません。出力先 directory には新規ファイルだけを作り、既存ファイルの置換や root 外の path を拒否します。

local MCPは許可したprojectだけを一覧に返し、復号したrecordと会話の読み取り、許可した場合の更新、原本転送、WAVプレビュー作成を提供します。project作成、端末承認、端末追加キー、OAuth token、秘密鍵、任意署名、許可拡大を扱うtoolはありません。各操作はローカルの許可・期限・端末状態を確認し、実APIがその要求の現在認可と失効を判定します。暗号処理は必要な操作で取得した同じ生成型の`CryptoReadBundle`を使い、独立した端末生存確認GETや毎操作のrefresh、定期ポーリングを挟みません。

catalogとrecord readは共通コアで公開鍵の系譜、署名、受理receiptを検証します。保持履歴を理由に無関係なprojectへの現在権限を要求しません。Root交換も同じコアのIdentity更新で処理し、準備済みstateと元の署名付き要求から再開します。scopeやgateのproof graph、Root交換専用manifestは使いません。

入力と出力は別のdirectoryを指定し、toolにはその配下の相対pathを渡します。絶対path、親参照、symlinkによる逸脱、既存出力の上書きを拒否します。安全なdescriptor操作を提供できないOSではfile toolを利用できません。Ctrl+C、期限切れ、worker切断で新規操作を止め、受付済みの処理を待ちます。更新が既に確定している可能性は残ります。復号した内容はMCP hostへ渡り、外部LLMを使えばその提供者にも開示されます。同じOSユーザーの悪意あるプログラムからの隔離は保証しません。

local MCP の汎用 `arteligo_write_record` と `arteligo_delete_record` は chat/comment の直接更新を `conversation_operation_required` で拒否します。会話では `arteligo_chat_send/edit/delete`、`arteligo_comment_create/edit/reply_create/reply_edit/resolution` を使います。origin と head に加え、chat の索引またはコメントの `CommentRevisionBinding` を同じ command に含めます。読み取りは `arteligo_chat_messages/events/message`、`arteligo_comment_threads/thread/replies/reply`、全履歴の明示検証は `arteligo_chat_message_history` です。コメントのページでは返却された `next_key` をそのまま `after` に渡します。ページ件数は正の整数とし、無効な revision と日時は session を開く前に拒否します。

broker は一つの AnyIO 実行環境と worker で操作を直列実行します。会話とファイル操作で実行寿命を切り替えず、受付済みの処理結果を返してから session を lock します。

内容の書き込みは生成型の`ValueMutation`と`RecordMutationBinding`で定義し、共通コアの`prepare`で署名付きprotobuf要求を作ります。recordの期待revisionとProtectionKeyを指定し、headと索引の更新を同じcommandへ含めます。受理receiptと元のCipherValueを検証してから復号し、保存済みの要求は同じoperation IDと元のbytesで再送します。

recordの削除は`deleted`属性を持つ新しいrevisionです。元のCipherValueと署名は書き換えません。署名対象を独自のcanonical JSONとして組み立てる処理や、旧形式を通常処理へ変換する経路はありません。

record の `expected_revision` と鍵世代は競合を検出するために必要です。`revision_conflict` の場合は現在の record を読み直してからユーザの変更を適用します。汎用 record 更新は自動的に再実行しません。会話 API は署名済みの操作 ID を確認し、競合した head と索引を読み直して最大 3 回まで再試行します。

実HTTP409の応答が `revision_conflict` を明示した場合、SDKは保存済みの元commandだけを共通暗号コアで解放します。コアの更新と対応するpendingの削除を保護保存してから、競合を呼び出し元へ返します。結果不明の通信失敗や一般403では解放しません。

## Python API

```python
from soenan_arteligo_support.e2ee import AcceptedCommand, EncryptedRecords, open_session
from soenan_arteligo_support.transfer import (
    download_file,
    upload_file,
    upload_wav_preview,
)


def main():
    session = open_session(
        account_origin="https://account.example",
        arteligo_origin="https://arteligo.example",
    )
    try:
        records = EncryptedRecords(session)
        selected = records.read("prj_example", ["fil_example"])
        result = upload_file(
            session, project_id="prj_example", source="./recording.wav"
        )
        if isinstance(result, AcceptedCommand):
            print("保存済みですが、端末内の後処理は未完了です。")
            return
        preview = upload_wav_preview(
            session,
            project_id="prj_example",
            file_id=result["file_id"],
            source="./recording.wav",
        )
        if isinstance(preview, AcceptedCommand):
            print("保存済みですが、端末内の後処理は未完了です。")
            return
        downloaded = download_file(
            session,
            project_id="prj_example",
            file_id=result["file_id"],
            destination="./downloaded.wav",
        )
        if isinstance(downloaded, AcceptedCommand):
            print("保存済みの操作がありますが、原本の公開は完了していません。")
            return
    finally:
        session.lock()


main()
```

`open_session`は認証と設定の取得を行い、保存済み端末があれば共通コアで設定のbundleを開いて`DeviceSession`を返します。途中で失敗した場合はsessionをlockして例外を返します。呼び出し側は返されたsessionを`finally`でlockします。起動時のOwner保守は行いません。

保存を伴う公開APIは、正常な値と`AcceptedCommand`を区別します。後者は検証済みの元command・resultと、後続処理の最初の例外を`finalization_error`に保持します。保存後の失敗を未保存へ戻したり、正常なproject ID・空配列・取得完了で代用したりしません。受理済みの場合は後続業務を止め、同じ保存済みoperationから再開します。

`AcceptedCommand`は要求された一連の処理全体の完了を意味しません。CLIとMCPは保存済みの事実と公開IDだけを表示し、署名証拠、例外原文、鍵を出力しません。

`download_file` の出力先は `destination` の path に限ります。認証・復号を終えた一時ファイルを新規出力として公開し、既存ファイルは上書きしません。内部の stream 復号処理は公開 API ではありません。MCP の出力は、許可済み directory の検証と公開を行う専用経路を使います。

`read` は指定した record だけを取得・復号します。`read_many` は指定した scope ごとに `read` を実行し、失敗した場合は例外を呼び出し側へ返します。鍵と証明は読み取り応答から受け取り、scope ごとの内容取得で全 project 一覧を読み直しません。

`current(scope, kind=..., after_record_id=..., limit=256)` は種類ごとの現在値、`changes(scope, after=..., limit=256)` は内容を含まない変更ページを返します。変更 cursor は署名・復号を確認済みの record revision ではありません。利用する内容は `read` で取得・検証します。

フォルダーは暗号化した header と B+tree を端末で解釈します。`EncryptedDirectory.page` は正の `limit` 件まで名前順で返し、既定の処理単位は 100 件です。続きは返却された `cursor` を渡します。folder の revision が変わると `revision_conflict` になるため、その folder の先頭から取り直します。アップロードは対象 folder の索引の枝と file record を一つの batch で更新し、他の folder の内容を読みません。

新規 project の独立した ProtectionKey は、現在の読者の受信鍵 U と、Owner 候補向けの事前配送先へ同じ command で封印します。候補向けの `owner_prepared` 配送は、その候補が現在 Owner になったときだけ取得できます。端末ごとに project 鍵を配り直さず、端末と U の配送、過去 P への直接配送、確定済み要求の再送は [鍵配布契約](../arteligo/docs/E2EE.md) に従います。

### 会話 API

`EncryptedConversations(records, scope, checkpoint=...)` は Flutter と同じ形式3の会話を扱います。新規 project では chat header と folder の索引を project 作成と同じ command で保存します。chat header がない project で chat を操作すると `content_format_update_required` を返します。`initialize()` は空の検証用 scope に chat header を明示作成する操作です。既存の会話を変換する機能はありません。

chat header の ID は `conversation_chat_header_<project ID>` です。不変の project ID を使い、異なる P の初期 record を同じ ID にしません。コメントは専用 header を作らず、`comments` または `file_view` の snapshot を読みます。IDL から生成した `CommentViewItem` と `CommentRevisionBinding` を使い、origin、thread head、body head、本文の revision、解決状態を扱います。

chat の message ID は `cmsg_` と32桁の小文字 hex です。新しい operation ID は英数字・`_`・`-` の1〜123文字で、`cevt_` を付けた record ID が公開契約の128 byte 内に収まる形式を使います。本文や参照の件数で内容を打ち切りません。タブ・改行以外の制御文字、不正な参照と重複した参照は拒否します。参照は `kind` と対応する `fileId`、`stageId`、`commentId`、`replyId` を持つ形式を使い、既存の署名済み本文や識別子を書き換えません。

```python
from soenan_arteligo_support.e2ee import EncryptedConversations

conversation = EncryptedConversations(records, "prj_0123456789abcdef0123456789abcdef")
page = conversation.chat_messages(limit=100)
if page["next_before_sequence"] is not None:
    older = conversation.chat_messages(before_sequence=page["next_before_sequence"])
conversation.write_chat(
    type="sent",
    message_id="cmsg_0123456789abcdef0123456789abcdef",
    operation_id="operation_unique_id",
    body="制作メモ",
    references=[],
    committed_at="2026-10-07T00:00:00Z",
)
```

| 操作 | メソッドとページ単位 |
| --- | --- |
| 最新メッセージと過去ページ | `chat_messages(before_sequence=..., limit=100)`、正の `limit` 件まで |
| イベントの取りこぼし | `chat_events(after=..., limit=200)`、正の `limit` 件まで |
| 1 メッセージと確定済み操作 | `chat_message(id)`、`chat_operation(operation_id)` |
| 送信、本文編集、削除 | `write_chat(type="sent"/"edited"/"deleted", ...)`。編集と削除は `expected_revision` 必須 |
| コメント一覧と返信ページ | `comment_threads(anchor=..., after=..., limit=100)`、`comment_replies(parent_id, after=..., limit=100)`、正の `limit` 件まで |
| コメントと返信 | `comment_thread(id)`、`comment_reply(id)`、`create_comment(id, value)`、`create_reply(id, parent_id=..., value=...)` |
| 本文編集と解決状態 | `edit_comment`、`edit_reply`、`set_resolution`。操作ごとに `operation_id` を渡す |
| 全履歴の明示検証 | `chat_message_history(id)`、`archive(snapshot_cursor=...)` |

通常のメッセージ表示は署名済み origin、現在の head、最新 event をまとめて取得します。編集履歴全体の列挙はしません。コメントも同じ snapshot の本文 head と最新の編集だけを取得します。origin、event、解決状態、本文編集、削除の terminal は immutable record として保存します。head と chat の索引、コメントの `CommentRevisionBinding` は、それぞれの操作と同じ CAS batch に含めます。受信した author と actor は署名元の account subject に照合します。

コメントの続きは生成型 `CommentCursor` の `sequence` と `id` で指定します。Pythonでは返却された `next_key` を `after` へそのまま渡し、local MCPでは同じ生成型のJSON表現を使います。単一IDの取得と更新前の確認は、先頭ページを列挙せず、そのIDと必要な親コメントだけを取得します。

応答を失った操作をやり直すときは、同じ message/comment/reply ID と `operation_id` を使います。確定済みの不変レコードを検証して結果を返し、暗号文の再生成や新しいイベントの追加を行いません。`checkpoint` は読み取り batch、保存の前後、検証ページの境界で呼びます。例外を投げると処理を止めます。保存後の取消は確定済みの操作を取り消さないため、同じ操作 ID で結果を確認します。

`EncryptedRecords.immutable_kind(scope, kind, after=..., snapshot_cursor=..., limit=256)` は immutable record を cursor 順で取得します。`limit` は正の件数で、256 は既定の処理単位です。最初のページの `snapshot_cursor` を後続の全ページと kind に渡すと、途中で追加された record を除外できます。`archive` はこの経路から会話を再構成し、固定の件数や平文 byte 数では拒否しません。欠けた証明や変化した snapshot は拒否します。個別に進捗や取消を管理する export は `immutable_kind` のページを直接処理でき、通常の画面表示から archive は呼びません。

ファイル名の検索・並べ替えはクライアントの処理です。サーバーへ名前、パス、検索文字列を渡す経路はありません。未取得の範囲を検索するアプリケーションは、通常の上限付き取得を使い、範囲・進捗・取消を管理します。SDK はプロジェクト全体の自動取得を行いません。

DEK はアップロードごとに端末で生成します。ProjectKey で包んだ DEK と詳細 manifest は encrypted file record に保存し、server の object manifest には object ID、鍵世代、暗号文サイズ、chunk index と checksum だけを送ります。Bucket へは暗号文だけを直接送信し、OAuth token は転送しません。

アップロード途中の情報は生成型 `FileUploadDraft` の暗号化 record `upl_` に保存します。begin と publish の署名済み command は送信前に保護保存し、応答を失った場合は同じ bytes を再送します。Bucket PUT 後の publish は、object の ready 状態、`FileMetadata`、locator、directory と draft の終了を同じ revision batch で確定します。公開済みなら原本を開き直さず、再暗号化・再 PUT もしません。確定的な directory revision 競合を、元 publish の再署名で回避しません。ダウンロードは全 chunk の checksum と AES-GCM 認証を終えてから、新しい保存先へ公開し、既存 file を上書きしません。

Flutter と SDK は同じ生成型 `FileMetadata` を `file_metadata` record に保存します。名前、日時、media 情報、原本と preview の object locator をこの型で扱います。ファイルの内容を独自の JSON 形式へ変換する中間層は置きません。

`upload_wav_preview` と local MCP の `arteligo_upload_wav_preview` は、元ファイルの暗号文 checksum と手元の WAV が一致することを確認し、ローカルの FFmpeg / FFprobe で Opus へ変換します。生成型 `PreviewUploadDraft` に preview の暗号化情報、元 object ID、元 file の revision を保存します。publish では `FileRevisionBinding` と `ObjectEffect` を同じ command に含め、file の preview 情報、object の ready 状態、draft の終了を原子的に更新します。応答を失った場合は、同じ file ID と WAV から保存済みの command を再送します。保留中の原本 publish を preview 公開済みとは判定しません。転送途中の再開では変換後の checksum を照合し、同じ鍵と nonce で異なる内容を送ることを防ぎます。preview の失敗は原本の保存を取り消しません。

転送は 8 MiB を既定の chunk 単位として進め、1,024 chunks や 8 GiB では打ち切りません。各 chunk の nonce と AAD が使う 32 bit の chunk index と、共通 wire 整数の正確な表現範囲は暗号契約として検証します。各 Bucket 要求には接続、読み取り、要求全体の期限があります。プレビューの変換と解析にも期限を設けます。暗号処理中のメモリは chunk 単位に限定し、使用後の可変バッファーは上書きします。Python の文字列や GC 内の複製まで消去できるとは保証しません。

## 契約と検証

HTTP 契約の正本は Arteligo の `contracts/openapi/arteligo-public.yaml` です。`generated/` はその契約から作る client で、手で変更しません。`GeneratedAPI` は生成済み endpoint と model を呼び出す transport adapter です。

ワークスペースのルートから、Swift・Dart・Python の生成物をまとめて更新します。protobuf の Python 実装と `.pyi` もこのコマンドで生成し、wheel に同梱します。生成物の一致は実サービスの動作を保証しません。

```sh
bin/soenan arteligo contract generate
```

SDK の手書き source、生成補助ツール、Journey driver はワークスペースのルートから `bin/soenan check` で検査します。Ruff の lint と format 差分、ty の型検査を実行します。規則はこのリポジトリの `pyproject.toml`、実行対象はワークスペースの `scripts/soenan_cli/commands/check.py` に定義しています。

SDK 本体と生成補助ツールは Python 3.10、Journey driver は Python 3.14 として検査します。ty は生成 protobuf の `.pyi` と導入済み package の型情報を使い、SDK の型付きインターフェースを検査します。生成 client の `generated/` は手書き source の lint・format 対象に含めません。静的検査は暗号・認可・転送の実サービス検証の代わりにはなりません。

SDKの業務検証には、配布packageとRust crypto runtime、実際のAccount・Arteligo・PostgreSQL・Bucketを使います。通常構成にValkeyはありません。通常クライアントでOAuthのブラウザー認証、OSの保護ストアへの保存、端末設定を行い、実際のファイルを保存・取得して内容を確認します。[workspaceのユーザフロー](../docs/local-development.md#利用者フローの確認)を参照してください。

micro・mock・fakeのsuite、大量metadataの生成・測定driver、専用DBus・keyring・native library環境、identity・source hash・証跡台帳を使うacceptance helperは削除しました。このリポジトリには、通常の認証からファイル転送までを自動確認するstandalone suiteはありません。
