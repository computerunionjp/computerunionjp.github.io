# 原稿取り込みツールの使い方

> 以下の説明ではディレクトリ（フォルダ）名の区切りに `/` （スラッシュ）を使っています。
> Windows で作業する場合は `\` （バックスラッシュ）または `¥` （半角の￥）に読み替えてください。

`drafts` の下に置かれた原稿（`*.md`）を、Front Matter の `categories`
（「しごと情報」または「ブログ」）に応じて適切な ID を採番し、`content`
の下に取り込みます。取り込みに成功したファイルは `drafts` から削除（画像
などの添付ファイルは移動）されます。

Python版 `tools/import.py` と PowerShell版 `tools/import.ps1` があり、
どちらも同じ動作をします。

## 1. Python版のセットアップ (初回のみ)

Python 3 の標準ライブラリのみを使用するため、セットアップは
[`tools/create.md`](create.md) の
「1. Python版のセットアップ」と同じです。

## 2. 実行方法

プロジェクトのルートディレクトリで実行してください。

### 2.1 Python版

```sh
$ ./.venv/bin/python tools/import.py
```

Mac OS のシステムの Python を使う場合は `python` を `python3` に
置き換えてください。

### 2.2 Windows PowerShell 5.1 / PowerShell 7

```powershell
PS> .\tools\import.ps1
```

または

```cmd
C:\...\computerunionjp> powershell.exe -File .\tools\import.ps1
```

```cmd
C:\...\computerunionjp> pwsh .\tools\import.ps1
```

または、エクスプローラ上でマウス右クリックして「PowerShell で実行」を
選択してください（手順の詳細は [`tools/create.md`](create.md) の
「2.2 Windows PowerShell 5.1」を参照してください）。

## 取り込みのルール

`drafts` の中身に応じて、次のいずれかの動作になります。

### 1. `drafts` に `*.md` が 1 つだけで、カテゴリが「ブログ」の場合

画像無し／画像有りを選択するプロンプトが表示されます。

```sh
$ ./.venv/bin/python tools/import.py
ブログの記事を取り込みます。
  2. ブログ（画像無し）
  3. ブログ（画像有り）
番号を入力してください (2～3): 2
drafts/draft.md を content/blog/8083.md としてインポートしました。
```

### 2. `drafts` に `*.md` が 1 つだけで、ほかに画像などのファイルがあり、カテゴリが「ブログ」の場合

プロンプトは表示されず、自動的に「画像有り」として取り込まれます。
`*.md` 以外のファイルは、取り込み先のディレクトリ（`index.md` と同じ
ディレクトリ）に移動されます。

```sh
$ ./.venv/bin/python tools/import.py
drafts/draft.md を content/blog/8083/index.md としてインポートしました。
drafts/photo.jpg を content/blog/8083/photo.jpg に移動しました。
```

### 3. `drafts` に `*.md` のみが複数（または 1 つで「ブログ」以外のカテゴリ）存在する場合

プロンプトは表示されず、各ファイルのカテゴリ（「しごと情報」または
「ブログ」）に応じて自動的に取り込み先が決まります。複数ファイルの場合
は、ID を 1 つずつ採番しながら順番に取り込みます。

```sh
$ ./.venv/bin/python tools/import.py
drafts/draft1.md を content/job/8083.md としてインポートしました。
drafts/draft2.md を content/job/8084.md としてインポートしました。
```

### 4. それ以外の場合は中止

- `drafts` が空、または存在しない場合
- `drafts` に `*.md` 以外のファイルが含まれていて、上記 1. 2. のいずれ
  にも当てはまらない場合（例: `*.md` が複数あり、かつ画像などのファイル
  も含まれている場合）

は、メッセージを表示して処理を中止します。ファイルは変更されません。

```sh
$ ./.venv/bin/python tools/import.py
drafts/ に *.md 以外のファイルが含まれているため、処理を中止します。
対象外のファイル: photo.jpg
```

## 注意事項

- 取り込み先の ID は、`content/blog` と `content/job` に存在する最大の
  数値 ID の次の番号が自動的に採番されます（[`tools/create.py`](create.py)
  /[`tools/create.ps1`](create.ps1) と同じ採番ルールです）。
- カテゴリを判定できない原稿（Front Matter に `categories` が無い、ある
  いは「しごと情報」「ブログ」のいずれでもない場合）はスキップされ、
  `drafts` に残ります。
- `drafts/.gitignore` により、`drafts` の中身（`.gitignore` 自体を除く）
  は Git の管理対象外です。
