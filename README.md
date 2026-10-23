# Arteligo のローカル E2EE クライアント

この SDK と local MCP は、利用者の承認済み端末として Arteligo の内容を暗号化・復号します。プロジェクト名、ファイル名、フォルダー構成、提出物、コメント、チャットなどは送信前に暗号化します。Arteligo と remote MCP は平文の鍵や内容を受け取りません。

Account が本人確認と OAuth を管理し、Arteligo が端末の承認状態、所属、権限、署名済み暗号文、revision、Bucket capability を管理します。暗号処理は Flutter と同じ `arteligo/native/e2ee` の Rust ライブラリーを使います。Python に別の HPKE や AES-GCM 実装はありません。

## 開発環境への導入

Python 3.10 以降と Rust toolchain が必要です。資格情報の保存には、package が依存する `keyring>=25.5` と、macOS Keychain、Windows Credential Manager、Linux Secret Service のいずれかを使います。平文ファイルへ保存する keyring backend へは切り替えません。

Linux では通常の user D-Bus と、利用可能な既定 collection を持つ Secret Service が必要です。SSH・TTY から使う場合も既存の user bus に接続し、本人の通常 keyring を先に解除します。GUI prompt を利用できない環境で別の bus・collection や平文 backend を作って代用しません。保護ストアを利用できない場合、`login` は OAuth 開始前に `secure_store_unavailable` で停止します。

端末鍵、信頼記録、再試行用の署名済み command は、暗号化した文書として端末内に保存します。OS の保護領域には固定サイズの復号鍵と確定済み文書への参照を置くため、journal が増えても Windows Credential Manager の項目容量を超えません。文書を永続化してから参照を置き換え、欠損・改ざん・保護鍵の喪失はエラーにします。保存済みの鍵を作り直したり、journal を空として扱ったりはしません。

ワークスペースのルートから、二つのローカル package を同時に導入します。

```sh
uv venv soenan-mcp-support/.venv
uv pip install --python soenan-mcp-support/.venv/bin/python ./arteligo/native/e2ee ./soenan-mcp-support
```

`arteligo-e2ee-native` のビルドは、固定した `Cargo.lock` で Rust ライブラリーを作り、実行環境用の wheel に同梱します。wheel は OS と CPU ごとに作ります。

## 端末の認証と承認

以下の `ACCOUNT_ORIGIN` と `ARTELIGO_ORIGIN` は対象環境の origin に置き換えます。HTTPS を使い、ローカル開発の loopback だけ HTTP を許可します。OAuth token は OS の保護領域へ保存します。端末の秘密鍵は OS の保護鍵で暗号化し、origin と account ごとに分離します。

```sh
arteligo --account-origin ACCOUNT_ORIGIN --arteligo-origin ARTELIGO_ORIGIN login
arteligo --account-origin ACCOUNT_ORIGIN --arteligo-origin ARTELIGO_ORIGIN status
```

`login` はブラウザーで Account の承認を開き、PKCE を使って loopback callback を受け取ります。ブラウザーへの認証情報入力は利用者が行います。CLI は固定の `arteligo-native-cli` public client と `arteligo:app` scope を使います。

同じ profile の OAuth 資格情報は、session や process ごとのコピーではなく、OS の保護領域にある一つの項目で管理します。refresh はその profile の process 間で調整し、単回利用の proof を送る前に保留状態を保存します。応答や最終保存の結果が不明な場合は、古い proof を再送しません。保護ストアが使えない場合も、平文ファイルやメモリーだけの保存へ切り替えません。

ブラウザーの操作待ちでは資格情報の lock を保持しません。同時に `login` を始めた場合は、最後に始めた操作だけが新しい資格情報を採用できます。code 交換の結果が不明なときは、以前の利用可能な資格情報を保持します。`logout` は先に古い操作を無効にし、既知の family の失効が保留中なら、それを解消するまで新しい login で上書きしません。同じ profile を古い SDK と同時に操作しないでください。旧形式の有効な access token は利用できても、refresh 可能な新形式へ自動昇格はしないため、再度 `login` が必要です。

session の置換を検出したら、その session が保持する署名・復旧・scope の鍵を利用できなくします。既に受付済みの要求まで取り消されたことにはせず、保存が確定した結果は保持します。project の読取り権限を失ったことが明示された場合は、その scope だけを回収します。一般の認証エラー、利用権の不足、見つからない応答を、project 全体の権限喪失とは扱いません。

最初の端末では `setup` を実行します。端末内で 256 bit の端末追加キーと独立した復旧鍵を生成し、キーから導出した鍵で暗号化した復旧 bundle だけを送信します。画面に表示された端末追加キーを安全な場所へ保存し、保存したキーを入力すると初期設定が完了します。キーを command argument、環境変数、MCP tool に渡しません。

追加端末では `add-by-key` を実行し、端末追加キーを入力します。新しい端末だけを `device_add_by_key` で登録し、既存端末・復旧 root・scope 世代は変えません。他の端末のオンライン承認、失効、追加キーの交換は要求しません。確認済みの復旧 root が既にある profile では、鍵束を開く前に現行 root の署名と両公開鍵を検証します。初めて追加する PC は、復号した鍵束の両公開鍵を照合した後にだけ現行 root を確定します。

`status` が `key_acquisition_pending` を返した場合は、同じ profile で `add-by-key` を再実行し、同じ端末から鍵の取得を再開します。入力を中断しても端末 ID と challenge を作り直しません。鍵取得が完了する前に端末が失効した場合、次の追加は新しい端末 ID と独立した鍵になります。

`add-by-key` が追加完了を表示するのは、端末内で署名と鍵取得を確認し、利用可能になった場合だけです。server の承認状態が `approved` でも、QR receipt の検証が済んでいなければ完了とは扱いません。Python API の `add_by_key` は `AdmissionResult.READY` または `AdmissionResult.KEY_ACQUISITION_PENDING` を返します。

既存端末で QR 承認を使う場合は、追加端末で `enroll` を実行し、出力された公開情報を承認済み端末へ直接渡します。既存端末で `approve --pairing-json pairing.json` を実行し、その receipt を追加端末へ戻します。追加端末で `accept-approval --receipt-json approval.json` を実行すると、challenge と両端末の公開鍵、承認署名を照合し、鍵転送を確認できます。Flutter の承認画面と同じ receipt を使います。

保存済みのheadから現行rootへの署名連鎖を検証できない場合は、`reanchor`を実行します。この端末の鍵素材だけを新しい端末IDで置き換え、確認済みの相手、rootの履歴、失効の観測は保持します。出力した公開情報を、新しいrootを確認済みの別端末で`approve`し、receiptを`accept-approval`へ戻します。検証できる正当なroot交換は通常の署名連鎖で追跡するため、交換のたびに再登録する必要はありません。

端末追加キーを交換する場合は、承認済み端末で `replace-addition-key` を実行します。新しいキーの保存確認後、新しい復旧 root 宛の envelope を現在読める organization と project の現行世代へ配り、復旧情報の交換と同時に保存します。viewer と archived の project も含めます。続けて、管理権限がある scope の鍵を更新します。承認済みの他端末は失効せず、新しい root へ進みます。

交換の途中で失敗すると、`status` の `recovery_replacement_pending` が `true` になります。同じ profile で `replace-addition-key` を再実行し、保存した新しいキーを入力すると、同じ交換を再開します。OS の保護領域に残すのは公開情報、暗号化した復旧 bundle、公開署名だけです。入力したキーや復旧鍵の秘密部分は保存しません。

中断中に別の承認済み端末が端末追加キーを交換していた場合は、最新の復旧情報の署名を確認して中断情報を解消し、`recovery_replacement_superseded` を返します。入力した古いキーの交換完了とは表示しません。必要なら `replace-addition-key` を再実行し、最新の復旧情報から新しいキーを発行します。

他の利用者の端末を直接確認したときは、その公開鍵への信頼を `peer_trust` の署名付き記録として保存します。端末追加キーや QR で追加した端末も、自分の承認済み端末の証明からこの記録を検証するため、server が返した未知の公開鍵を自動的に信頼しません。公開証明には暗号化済みの復旧 bundle を含めません。

## local MCP

MCP host は、人が開始した `mcp-grant` が表示する worker の stdio command を使います。`mcp` は短命 handle がないと起動しません。

```sh
arteligo --account-origin ACCOUNT_ORIGIN --arteligo-origin ARTELIGO_ORIGIN \
  mcp-grant --project PROJECT_ID --access read-only --expires-in 3600 \
  [--input-dir INPUT_DIRECTORY] [--output-dir OUTPUT_DIRECTORY]
```

`mcp-grant` は前景で許可対象を表示し、人が `authorize` を入力した後だけ handle を発行します。対象は明示した既存 project、`read-only` または `update` の範囲、期限、任意の入出力 directory に固定し、実行中に拡大できません。端末の承認状態は各操作の前に再確認し、失効した端末の session を使い続けません。worker は通常の OAuth token や端末追加キーを受け取りません。出力先 directory には新規ファイルだけを作り、既存ファイルの置換や root 外の path を拒否します。

local MCPは許可したprojectだけを一覧に返し、復号したrecordと会話の読み取り、許可した場合の更新、原本転送、WAVプレビュー作成を提供します。project作成、端末承認、端末追加キー、OAuth token、秘密鍵、任意署名、許可拡大を扱うtoolはありません。各操作の前に現在の端末承認と認可を確認します。定期ポーリングは行いません。

入力と出力は別のdirectoryを指定し、toolにはその配下の相対pathを渡します。絶対path、親参照、symlinkによる逸脱、既存出力の上書きを拒否します。安全なdescriptor操作を提供できないOSではfile toolを利用できません。Ctrl+C、期限切れ、worker切断で新規操作を止め、受付済みの処理を待ちます。更新が既に確定している可能性は残ります。復号した内容はMCP hostへ渡り、外部LLMを使えばその提供者にも開示されます。同じOSユーザーの悪意あるプログラムからの隔離は保証しません。

local MCP の汎用 `arteligo_write_record` と `arteligo_delete_record` は chat/comment の直接更新を `conversation_operation_required` で拒否します。会話では `arteligo_chat_send/edit/delete`、`arteligo_comment_create/edit/reply_create/reply_edit/resolution` を使い、origin、head、索引を同じ batch に保存します。読み取りは `arteligo_chat_messages/events/message`、`arteligo_comment_threads/thread/replies/reply`、全履歴の明示検証は `arteligo_chat_message_history` です。コメントのページでは返却された `next_key` をそのまま `after` に渡します。ページ件数は正の整数とし、無効な revision と日時は session を開く前に拒否します。

broker は一つの AnyIO 実行環境と worker で操作を直列実行します。会話とファイル操作で実行寿命を切り替えず、受付済みの処理結果を返してから session を lock します。

内容の書き込みは、chat/comment を含む batch が形式 3、その他が形式 2 です。初回受付の期限と読み取った record の期待 revision を署名に含めます。SDK が設定する期限は作成から 29 日後で、確定結果はサーバーが 30 日間保持します。保存応答が分割された場合は cursor の進行を確認しながら残りを読み取り、送信した全 record の revision、暗号文、署名を検証してから成功を返します。応答を揃えられない場合は更新を再送せず、保存結果が未確認であることを返します。record の平文や署名する command body に、512 KiB や 1 MiB の受付上限は設けません。

record の削除は `record_id`、`kind`、`expected_revision`、`key_epoch`、`deleted: true` のみを持つ署名済み marker です。marker には暗号文や `value` がなく、以前の有料の内容を一度だけ退役させます。marker を含む command 全体には公開された canonical JSON 表現を使います。以前に保存した暗号文付きの削除 record は、元の署名と暗号文のまま検証・復号し、読み取り専用の履歴として扱います。

record の `expected_revision` と鍵世代は競合を検出するために必要です。`revision_conflict` の場合は現在の record を読み直してから利用者の変更を適用します。汎用 record 更新は自動的に再実行しません。会話 API は署名済みの操作 ID を確認し、競合した head と索引を読み直して最大 3 回まで再試行します。

## Python API

```python
from soenan_arteligo_support.e2ee import EncryptedDirectory, EncryptedRecords, open_session
from soenan_arteligo_support.transfer import download_file, upload_file, upload_wav_preview

session = open_session(
    account_origin="https://account.example",
    arteligo_origin="https://arteligo.example",
)
try:
    records = EncryptedRecords(session)
    page = EncryptedDirectory(records, "prj_example").page(limit=100)
    selected = records.read("prj_example", ["fil_example"])
    result = upload_file(session, project_id="prj_example", source="./recording.wav")
    upload_wav_preview(
        session,
        project_id="prj_example",
        file_id=result["file_id"],
        source="./recording.wav",
    )
    download_file(
        session,
        project_id="prj_example",
        file_id=result["file_id"],
        destination="./downloaded.wav",
    )
finally:
    session.lock()
```

`open_session` が失敗した場合は、作成途中の session を lock して例外を返します。正常に返された session は、呼び出し側が `finally` で lock します。

`download_file` の出力先は `destination` の path に限ります。認証・復号を終えた一時ファイルを新規出力として公開し、既存ファイルは上書きしません。内部の stream 復号処理は公開 API ではありません。MCP の出力は、許可済み directory の検証と公開を行う専用経路を使います。

`read` は指定した record だけを取得・復号します。`read_many` は複数 scope の概要などを一括で取得でき、ある scope の認可・鍵・検証の失敗を他の scope の結果から分離します。同じ署名付き command は応答内で一度検証します。鍵と証明は読み取り応答から受け取り、scope ごとの内容取得で全 project 一覧を読み直しません。

`current(scope, kind=..., after_record_id=..., limit=256)` は種類ごとの現在値、`changes(scope, after=..., limit=256)` は内容を含まない変更ページを返します。変更 cursor は署名・復号を確認済みの record revision ではありません。利用する内容は `read` で取得・検証します。

フォルダーは暗号化した header と B+tree を端末で解釈します。`EncryptedDirectory.page` は正の `limit` 件まで名前順で返し、既定の処理単位は 100 件です。続きは返却された `cursor` を渡します。folder の revision が変わると `revision_conflict` になるため、その folder の先頭から取り直します。アップロードは対象 folder の索引の枝と file record を一つの batch で更新し、他の folder の内容を読みません。

新規projectの鍵は作成中の一端末だけでなく、検証済みの承認済み自己端末と現行の復旧先へ同じcommandで配ります。現在の端末状態と署名証明を区別し、初期配布の完全性・組織envelope・確定済み再送は[鍵配布契約](../arteligo/docs/E2EE.md)に従います。

### 会話 API

`EncryptedConversations(records, scope, checkpoint=...)` は Flutter と同じ会話形式 3 を読み書きします。新規 project は、空の会話 header 2 個と folder の索引を project 作成と同じ command で保存します。header がない project の通常操作は `content_format_update_required` を返します。`initialize()` は空の検証用 scope に header を明示作成する操作です。既存の会話を変換する機能はありません。

chat の message ID は `cmsg_` と32桁の小文字 hex です。新しい operation ID は英数字・`_`・`-` の1〜123文字で、`cevt_` を付けた record ID が公開契約の128 byte 内に収まる形式を使います。本文や参照の件数で内容を打ち切りません。タブ・改行以外の制御文字、不正な参照と重複した参照は拒否します。参照は `kind` と対応する `fileId`、`stageId`、`commentId`、`replyId` を持つ形式を使い、既存の署名済み本文や識別子を書き換えません。

```python
from soenan_arteligo_support.e2ee import EncryptedConversations

conversation = EncryptedConversations(records, "prj_0123456789abcdef0123456789abcdef")
page = conversation.chat_messages(limit=100)
if page["next_before_sequence"] is not None:
    older = conversation.chat_messages(before_sequence=page["next_before_sequence"])
conversation.write_chat(
    type="sent", message_id="cmsg_0123456789abcdef0123456789abcdef", operation_id="operation_unique_id",
    body="制作メモ", references=[], committed_at="2026-10-07T00:00:00Z",
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

通常のメッセージ表示は、署名済み origin、現在の head、最新 event をまとめて取得します。編集履歴全体の列挙はしません。コメントも本文 head と最新の編集だけを取得します。origin、event、解決状態、本文編集、削除の terminal は immutable record として保存し、head と索引の更新は同じ CAS batch に含めます。受信した author と actor は署名元の account subject に照合します。

応答を失った操作をやり直すときは、同じ message/comment/reply ID と `operation_id` を使います。確定済みの不変レコードを検証して結果を返し、暗号文の再生成や新しいイベントの追加を行いません。`checkpoint` は読み取り batch、保存の前後、検証ページの境界で呼びます。例外を投げると処理を止めます。保存後の取消は確定済みの操作を取り消さないため、同じ操作 ID で結果を確認します。

`EncryptedRecords.immutable_kind(scope, kind, after=..., snapshot_cursor=..., limit=256)` は immutable record を cursor 順で取得します。`limit` は正の件数で、256 は既定の処理単位です。最初のページの `snapshot_cursor` を後続の全ページと kind に渡すと、途中で追加された record を除外できます。`archive` はこの経路から会話を再構成し、固定の件数や平文 byte 数では拒否しません。欠けた証明や変化した snapshot は拒否します。個別に進捗や取消を管理する export は `immutable_kind` のページを直接処理でき、通常の画面表示から archive は呼びません。

ファイル名の検索・並べ替えはクライアントの処理です。サーバーへ名前、パス、検索文字列を渡す経路はありません。未取得の範囲を検索するアプリケーションは、通常の上限付き取得を使い、範囲・進捗・取消を管理します。SDK はプロジェクト全体の自動取得を行いません。

DEK はアップロードごとに端末で生成します。ProjectKey で包んだ DEK と詳細 manifest は encrypted file record に保存し、server の object manifest には object ID、鍵世代、暗号文サイズ、chunk index と checksum だけを送ります。Bucket へは暗号文だけを直接送信し、OAuth token は転送しません。

アップロード途中の情報は暗号化した`upl_` recordに保存します。ready前の再開では、`upload_id`と同じローカルファイルを指定し、内容の変更をchecksumで拒否します。objectが`ready`なら原本を開き直さず、再暗号化・再PUTをせずに、確定fileとdirectory recordの公開を同じrevision batchで完了します。保存の完了応答を失った場合も同じfile IDを返し、一覧の項目を増やしません。directoryとの競合では同じ`upload_id`で再実行します。ダウンロードは全chunkのchecksumとAES-GCM認証を終えてから、新しい保存先へ公開し、既存fileを上書きしません。

`upload_wav_preview` と local MCP の `arteligo_upload_wav_preview` は、元ファイルの暗号文 checksum と手元の WAV が一致することを確認し、ローカルの FFmpeg / FFprobe で Opus に変換します。プレビュー専用の DEK を生成し、送信前に object ID、manifest、包んだ DEK を暗号化した file record に保存します。再生情報と音量解析も同じ record に保存するため、Flutter でも同じプレビューを再生できます。転送や保存の応答を失った場合は、同じ file ID と WAV を指定して再開します。object が `ready` なら変換と転送を繰り返さず、record の保存を完了します。転送途中の再開では変換後の checksum を照合し、同じ鍵と nonce で異なる内容を送ることを防ぎます。変換の失敗は元ファイルの保存を取り消しません。

転送は 8 MiB を既定の chunk 単位として進め、1,024 chunks や 8 GiB では打ち切りません。各 chunk の nonce と AAD が使う 32 bit の chunk index と、共通 wire 整数の正確な表現範囲は暗号契約として検証します。各 Bucket 要求には接続、読み取り、要求全体の期限があります。プレビューの変換と解析にも期限を設けます。暗号処理中のメモリは chunk 単位に限定し、使用後の可変バッファーは上書きします。Python の文字列や GC 内の複製まで消去できるとは保証しません。

## 契約と検証

HTTP 契約の正本は Arteligo の `contracts/openapi/arteligo-public.yaml` です。`generated/` はその契約から作る client で、手で変更しません。`GeneratedAPI` は生成済み endpoint と model を呼び出す transport adapter です。

ワークスペースのルートから、Swift・Dart・Python の生成物をまとめて更新します。生成物の一致は実サービスの動作を保証しません。

```sh
bin/soenan arteligo contract generate
```

SDKの手書きsourceは、ワークスペースのルートから`bin/soenan check`で静的検査します。Ruff F規則とPython 3.10の対象設定は、このリポジトリの`pyproject.toml`が管理します。生成clientの`generated/`は除外します。未定義名や未使用importの検出は、暗号・認可・転送の実サービス検証の代わりにはなりません。

SDKの業務検証には、配布packageとRust crypto runtime、実際のAccount・Arteligo・PostgreSQL・Bucketを使います。通常構成にValkeyはありません。通常クライアントでOAuthのブラウザー認証、OSの保護ストアへの保存、端末設定を行い、実際のファイルを保存・取得して内容を確認します。[workspaceの利用者フロー](../docs/local-development.md#利用者フローの確認)を参照してください。

micro・mock・fakeのsuite、大量metadataの生成・測定driver、専用DBus・keyring・native library環境、identity・source hash・証跡台帳を使うacceptance helperは削除しました。このリポジトリには、通常の認証からファイル転送までを自動確認するstandalone suiteはありません。
