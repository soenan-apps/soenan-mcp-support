# Arteligo のローカル E2EE クライアント

この SDK と local MCP は、利用者の承認済み端末として Arteligo の内容を暗号化・復号します。プロジェクト名、ファイル名、フォルダー構成、提出物、コメント、チャットなどは送信前に暗号化します。Arteligo と remote MCP は平文の鍵や内容を受け取りません。

Account が本人確認と OAuth を管理し、Arteligo が端末の承認状態、所属、権限、署名済み暗号文、revision、Bucket capability を管理します。暗号処理は Flutter と同じ `arteligo/native/e2ee` の Rust ライブラリーを使います。Python に別の HPKE や AES-GCM 実装はありません。

## 開発環境への導入

Python 3.10 以降と Rust toolchain が必要です。macOS Keychain、Windows Credential Manager、Linux Secret Service のいずれかを使います。平文ファイルへ保存する keyring backend へは切り替えません。

ワークスペースのルートから、二つのローカル package を同時に導入します。

```sh
uv venv soenan-mcp-support/.venv
uv pip install --python soenan-mcp-support/.venv/bin/python ./arteligo/native/e2ee ./soenan-mcp-support
```

`arteligo-e2ee-native` のビルドは、固定した `Cargo.lock` で Rust ライブラリーを作り、実行環境用の wheel に同梱します。wheel は OS と CPU ごとに作ります。

## 端末の認証と承認

以下の `ACCOUNT_ORIGIN` と `ARTELIGO_ORIGIN` は対象環境の origin に置き換えます。HTTPS を使い、ローカル開発の loopback だけ HTTP を許可します。OAuth token と端末の秘密鍵は OS の保護領域へ保存し、origin と account ごとに分離します。

```sh
arteligo --account-origin ACCOUNT_ORIGIN --arteligo-origin ARTELIGO_ORIGIN login
arteligo --account-origin ACCOUNT_ORIGIN --arteligo-origin ARTELIGO_ORIGIN status
```

`login` はブラウザーで Account の承認を開き、PKCE を使って loopback callback を受け取ります。ブラウザーへの認証情報入力は利用者が行います。CLI は固定の `arteligo-native-cli` public client と `arteligo:app` scope を使います。

最初の端末では `setup` を実行します。端末内で 256 bit の復旧コードと独立した復旧鍵を生成し、コードで暗号化した復旧 bundle だけを送信します。画面に表示された復旧コードを安全な場所へ保存し、保存したコードを入力すると初期設定が完了します。コードを command argument、環境変数、MCP tool に渡しません。

追加端末では `enroll` を実行し、出力された公開情報を既存の承認済み端末へ直接渡します。既存端末で `approve --pairing-json pairing.json` を実行し、その公開情報の receipt を追加端末へ戻します。追加端末で `accept-approval --receipt-json approval.json` を実行すると、challenge と両端末の公開鍵、承認署名を照合し、鍵転送を確認できます。Flutter の承認画面と同じ receipt を使います。

既存端末を使えない場合は `recover` を実行し、端末上で復旧コードを入力します。復旧コードは server に送らず、ローカルで復旧鍵を開き、新しい端末用の独立した鍵を生成します。復旧鍵の秘密部分は通常の端末鍵として保存しません。

`recover` は、復旧した鍵を新しい端末へ保存し、管理権限がある organization と project の鍵を更新してから完了します。途中で失敗すると `status` は `recovery_pending` を返します。同じ profile で `recover` を再実行し、復旧コードを入力すると、同じ新端末から再開します。復旧コードや復旧鍵の秘密部分を再開情報へ保存することはありません。閲覧者として参加している scope の鍵更新は、その scope の管理権限がある参加者が行います。

復旧コードを置き換える場合は、承認済み端末で `replace-recovery` を実行します。新しいコードの保存確認後、読み取れる organization と project の現行鍵を新しい復旧鍵で包み、復旧情報の交換と同時に保存します。閲覧者として参加している project とアーカイブ済みの project も含めます。続けて、管理権限がある scope の鍵を更新します。交換前のコードは失効します。新しいコードから復旧した端末は、過去の project 鍵と、失効済み端末が署名した履歴も検証できます。

交換の途中で失敗すると、`status` の `recovery_replacement_pending` が `true` になります。同じ profile で `replace-recovery` を再実行し、保存した新しいコードを入力すると、同じ復旧情報の交換を再開します。OS の保護領域に残すのは公開情報、暗号化した復旧 bundle、公開署名だけです。復旧コードや復旧鍵の秘密部分は保存しません。

中断中に別の承認済み端末が復旧コードを交換していた場合は、最新の復旧情報の署名を確認して中断情報を解消し、`recovery_replacement_superseded` を返します。入力した古いコードの交換完了とは表示しません。必要なら `replace-recovery` を再実行し、最新の復旧情報から新しいコードを発行します。

他の利用者の端末を直接確認したときは、その公開鍵への信頼を `peer_trust` の署名付き記録として保存します。復旧後は自分の承認済み端末の証明からこの記録を検証するため、server が返した未知の公開鍵を自動的に信頼しません。公開証明には暗号化済みの復旧 bundle を含めません。

## local MCP

MCP host の stdio server command に次を設定します。`--profile` を指定すると同じコンピューター上で保存先を分けられます。

```sh
arteligo --account-origin ACCOUNT_ORIGIN --arteligo-origin ARTELIGO_ORIGIN mcp
```

local MCP はプロジェクト一覧、復号した record の読み取り・更新、プロジェクト作成、ローカルファイルのアップロードとダウンロード、WAV の音声プレビュー作成を提供します。端末承認、復旧コード、OAuth token、秘密鍵を扱う操作は MCP tools に含めません。各要求で承認状態を確認し、認証を要する呼び出し時だけ必要に応じて OAuth token を更新します。新しい処理を探す定期ポーリングはありません。

record の平文上限は 512 KiB、署名する command body は 1 MiB です。内容の書き込みは形式 2、初回受付の期限、読み取った record の期待 revision を署名に含めます。SDK が設定する期限は作成から 29 日後で、確定結果はサーバーが 30 日間保持します。大きな batch の保存応答が分割された場合は、返却済み cursor から最大 16 ページを読み直し、送信した全 record の revision、暗号文、署名を検証してから成功を返します。応答を揃えられない場合は更新を再送せず、保存結果が未確認であることを返します。

record の `expected_revision` と鍵世代は競合を検出するために必要です。`revision_conflict` の場合は現在の record を読み直してから利用者の変更を適用します。更新を自動的に再実行しません。

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

`read` は指定した最大 256 record だけを取得・復号します。`read_many` は最大 32 scopes の概要などを一括で取得でき、ある scope の認可・鍵・検証の失敗を他の scope の結果から分離します。同じ署名付き command は応答内で一度検証します。鍵と証明は読み取り応答から受け取り、scope ごとの内容取得で全 project 一覧を読み直しません。

`current(scope, kind=..., after_record_id=..., limit=256)` は種類ごとの現在値、`changes(scope, after=..., limit=256)` は内容を含まない変更ページを返します。変更 cursor は署名・復号を確認済みの record revision ではありません。利用する内容は `read` で取得・検証します。

フォルダーは暗号化した header と B+tree を端末で解釈します。`EncryptedDirectory.page` は既定 100 件、最大 200 件を名前順で返し、続きは返却された `cursor` を渡します。folder の revision が変わると `revision_conflict` になるため、その folder の先頭から取り直します。アップロードは対象 folder の索引の枝と file record を一つの batch で更新し、他の folder の内容を読みません。

旧 directory 形式は `migrate_directory(records, scope, maximum_batches=64)` または local MCP の `arteligo_migrate_directory` で変換します。移行中は通常の内容更新を止め、暗号化した checkpoint から再開します。新しい root を公開するまで旧 directory を保持し、公開後に旧 record を回収します。返り値の `complete` が `false` なら、同じ project を指定して続きを実行します。既存 file ID と Bucket object は変わりません。

公開前の移行を取り消す場合は `abort_directory_migration` または local MCP の `arteligo_abort_directory_migration` を使います。移行で作った node だけを最大 128 件ずつ回収し、最後に checkpoint を最小の tombstone に置き換えて通常更新を再開します。取消の途中も同じ操作で再開でき、旧 directory と file は保持します。公開済みの root はこの操作では取り消せません。

ファイル名の検索・並べ替えはクライアントの処理です。サーバーへ名前、パス、検索文字列を渡す経路はありません。未取得の範囲を検索するアプリケーションは、通常の上限付き取得を使い、範囲・進捗・取消を管理します。SDK はプロジェクト全体の自動取得を行いません。

DEK はアップロードごとに端末で生成します。ProjectKey で包んだ DEK と詳細 manifest は encrypted file record に保存し、server の object manifest には object ID、鍵世代、暗号文サイズ、chunk index と checksum だけを送ります。Bucket へは暗号文だけを直接送信し、OAuth token は転送しません。

アップロード途中の情報は暗号化した `upl_` record に保存します。失敗後は `upload_id` と同じローカルファイルを明示して再開できます。内容が変わったファイルは checksum の照合で拒否します。object が `ready` なら転送を繰り返さず、元ファイルと directory record の保存から再開します。これらは同じ revision batch で保存します。保存の完了応答を失った場合も、再実行で同じ file ID を返し、一覧の項目を増やしません。directory の更新と競合した場合は、同じ `upload_id` で再実行します。ダウンロードは全 chunk の checksum と AES-GCM 認証を終えてから、新しい保存先へファイルを公開します。既存ファイルを上書きしません。

`upload_wav_preview` と local MCP の `arteligo_upload_wav_preview` は、元ファイルの暗号文 checksum と手元の WAV が一致することを確認し、ローカルの FFmpeg / FFprobe で Opus に変換します。プレビュー専用の DEK を生成し、送信前に object ID、manifest、包んだ DEK を暗号化した file record に保存します。再生情報と音量解析も同じ record に保存するため、Flutter でも同じプレビューを再生できます。転送や保存の応答を失った場合は、同じ file ID と WAV を指定して再開します。object が `ready` なら変換と転送を繰り返さず、record の保存を完了します。転送途中の再開では変換後の checksum を照合し、同じ鍵と nonce で異なる内容を送ることを防ぎます。変換の失敗は元ファイルの保存を取り消しません。

転送上限は 1,024 chunks、chunk あたり最大 8 MiB の平文、object あたり最大 8 GiB の暗号文です。各 Bucket 要求には接続、読み取り、要求全体の期限があります。プレビューの変換と解析にも期限を設けます。暗号処理中のメモリは chunk 単位に限定し、使用後の可変バッファーは上書きします。Python の文字列や GC 内の複製まで消去できるとは保証しません。

## 契約と検証

HTTP 契約の正本は Arteligo の `contracts/openapi/arteligo-public.yaml` です。`generated/` はその契約から作る client で、手で変更しません。`GeneratedAPI` は生成済み endpoint と model を呼び出す transport adapter です。

```sh
uvx --from openapi-python-client==0.28.0 --with ruff==0.16.9 openapi-python-client generate --path ../arteligo/contracts/openapi/arteligo-public.yaml --meta none --output-path generated/arteligo_public_api_client --overwrite
.venv/bin/python -m pytest -q
```

検証では、共通 Rust core の既知値、独立端末への承認、双方向の公開鍵確認、復旧コード、公開鍵の差し替え、過去世代の鍵の復旧、署名と暗号文の改ざん、実際の loopback Bucket 転送、保存先の原子的な公開を確認します。テストは実際の Keychain や Account の認証情報を使いません。

ローカルスタックのブラウザー性能検証には、ワークスペースの `bin/soenan local acceptance arteligo-browser-metadata prepare` を使います。`--cdp-url` で承認済み端末を持つブラウザー、`--origin` でローカル Arteligo、`--entries` で件数、`--manifest` で公開情報だけの検証記録を指定します。既存のブラウザー認証と保護済み端末情報をメモリー内だけで使い、専用プロジェクトに署名・暗号化した file metadata とフォルダー索引を作ります。既定では概要一覧の測定用に空のプロジェクトも 49 件作り、各プロジェクトの削除用 manifest を親の `overview_fixture_manifests` から参照します。既存プロジェクトは変更しません。

この fixture は Bucket object を作らないため、一覧の表示・復号・ページングを測定するためのものです。ファイルのダウンロードは検証できません。中断した場合も manifest に残る `scope_id` が削除対象になります。検証後はワークスペース側でその専用 scope を削除します。`check` は保存済み manifest を使って先頭と続きの各 100 件を読み、HTTP 回数、応答バイト数、所要時間を記録します。

作成要求の前に公開情報だけの manifest を保存します。作成応答を失った場合は、`archive` が対象 scope の署名付き作成証明を読み直して回収を続けます。作成が確認できない場合は manifest を残し、完了扱いにしません。`archive` 後の `cleanup` はワークスペース側で作成証明と所有者を検査し、専用 scope のメタデータと利用量を回収します。

同じ入口の `benchmark` は、認証済みプロジェクト一覧、先頭 32 project の一括概要取得、fixture の file metadata 先頭 100 件を測定します。既定は同時接続数 1・8・16、各 30 秒、各 3 回です。`--output` へ応答件数、HTTP status、失敗、認証更新回数、応答バイト数、p50・p95 を保存します。Cookie はブラウザー内の要求だけに使い、端末鍵は読み取りません。負荷測定は UI の時間測定や大量データ生成と分けて実行します。
