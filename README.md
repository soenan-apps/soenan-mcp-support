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

復旧コードを置き換える場合は、承認済み端末で `replace-recovery` を実行します。新しいコードの保存確認後、既存端末の公開鍵を新しい復旧鍵で証明し、organization と project の現行鍵を更新します。交換前のコードは失効します。新しいコードから復旧した端末は、過去の project 鍵と、失効済み端末が署名した履歴も検証できます。

他の利用者の端末を直接確認したときは、その公開鍵への信頼を `peer_trust` の署名付き記録として保存します。復旧後は自分の承認済み端末の証明からこの記録を検証するため、server が返した未知の公開鍵を自動的に信頼しません。公開証明には暗号化済みの復旧 bundle を含めません。

## local MCP

MCP host の stdio server command に次を設定します。`--profile` を指定すると同じコンピューター上で保存先を分けられます。

```sh
arteligo --account-origin ACCOUNT_ORIGIN --arteligo-origin ARTELIGO_ORIGIN mcp
```

local MCP はプロジェクト一覧、復号した record の読み取り・更新、プロジェクト作成、ローカルファイルのアップロードとダウンロード、WAV の音声プレビュー作成を提供します。端末承認、復旧コード、OAuth token、秘密鍵を扱う操作は MCP tools に含めません。各要求で承認状態を確認し、認証を要する呼び出し時だけ必要に応じて OAuth token を更新します。新しい処理を探す定期ポーリングはありません。

record の平文上限は 512 KiB、署名する command body は 1 MiB です。大きな batch の保存応答が分割された場合は、返却済み cursor から最大 16 ページを読み直し、送信した全 record の revision、暗号文、署名を検証してから成功を返します。応答を揃えられない場合は更新を再送せず、保存結果が未確認であることを返します。

record の `expected_revision` と鍵世代は競合を検出するために必要です。`revision_conflict` の場合は現在の record を読み直してから利用者の変更を適用します。更新を自動的に再実行しません。

## Python API

```python
from soenan_arteligo_support.e2ee import EncryptedRecords, open_session
from soenan_arteligo_support.transfer import download_file, upload_file, upload_wav_preview

session = open_session(
    account_origin="https://account.example",
    arteligo_origin="https://arteligo.example",
)
try:
    records = EncryptedRecords(session)
    page = records.page("prj_example", after=0, limit=128)
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

DEK はアップロードごとに端末で生成します。ProjectKey で包んだ DEK と詳細 manifest は encrypted file record に保存し、server の object manifest には object ID、鍵世代、暗号文サイズ、chunk index と checksum だけを送ります。Bucket へは暗号文だけを直接送信し、OAuth token は転送しません。

アップロード途中の情報は暗号化した `upl_` record に保存します。失敗後は `upload_id` と同じローカルファイルを明示して再開できます。内容が変わったファイルは checksum の照合で拒否します。元ファイルと directory record は、object の完了後に同じ revision batch で保存します。ダウンロードは全 chunk の checksum と AES-GCM 認証を終えてから、新しい保存先へファイルを公開します。既存ファイルを上書きしません。

`upload_wav_preview` と local MCP の `arteligo_upload_wav_preview` は、元ファイルの暗号文 checksum と手元の WAV が一致することを確認し、ローカルの FFmpeg / FFprobe で Opus に変換します。プレビュー専用の DEK を生成し、暗号文だけを別 object として送信します。再生情報、音量解析、包んだ DEK は暗号化した file record に保存するため、Flutter でも同じプレビューを再生できます。作成済みのプレビューは再利用します。変換の失敗は元ファイルの保存を取り消さず、同じ file ID で明示的に再試行できます。

転送上限は 1,024 chunks、chunk あたり最大 8 MiB の平文、object あたり最大 8 GiB の暗号文です。各 Bucket 要求には接続、読み取り、要求全体の期限があります。プレビューの変換と解析にも期限を設けます。暗号処理中のメモリは chunk 単位に限定し、使用後の可変バッファーは上書きします。Python の文字列や GC 内の複製まで消去できるとは保証しません。

## 契約と検証

HTTP 契約の正本は Arteligo の `contracts/openapi/arteligo-public.yaml` です。`generated/` はその契約から作る client で、手で変更しません。`GeneratedAPI` は生成済み endpoint と model を呼び出す transport adapter です。

```sh
uvx --from openapi-python-client==0.28.0 --with ruff==0.16.9 openapi-python-client generate --path ../arteligo/contracts/openapi/arteligo-public.yaml --meta none --output-path generated/arteligo_public_api_client --overwrite
.venv/bin/python -m pytest -q
```

検証では、共通 Rust core の既知値、独立端末への承認、双方向の公開鍵確認、復旧コード、公開鍵の差し替え、過去世代の鍵の復旧、署名と暗号文の改ざん、実際の loopback Bucket 転送、保存先の原子的な公開を確認します。テストは実際の Keychain や Account の認証情報を使いません。
