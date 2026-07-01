# 移行ツールの使い方

[前提と要件](../migration/01requirements.md) に従って `migration/imports/WordPress.xml`
(WordPress のエクスポート XML / WXR 形式) を、Hugo の `contentDir` (`src`) 以下の
Markdown へ変換するインポートツールです。実装は `tools` にあります。

## 1. セットアップ (初回のみ)

Python 3 の `venv` を使います。プロジェクトのルートディレクトリ (`hugo.toml` がある場所) で
実行してください。

```sh
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## 2. 実行方法

同じくプロジェクトのルートディレクトリで実行してください。

```sh
./venv/bin/python tools/import_wordpress.py
```

実行すると `migration/imports/WordPress.xml` を読み込み、`src` 以下に Markdown ファイルと
画像・添付ファイルを生成します。既存の生成結果 (`src/blog`, `src/job`, `src/pages`,
`src/errors`, `src/images`, `src/contact.md`) は実行のたびに一度削除してから作り直すため、
何度でも再実行できます (`src/_index.md` など、ツールが生成しないファイルは削除されません)。

実行後、コンソールに種別ごとの件数と、`src/errors` へ振り分けられた記事の一覧、
ダウンロードに失敗した画像・添付ファイルの一覧が表示されます。

### 主なオプション

| オプション | 説明 |
| --- | --- |
| `--input PATH` | 入力する WXR ファイルのパス (既定: `migration/imports/WordPress.xml`) |
| `--output PATH` | 出力先ディレクトリ (既定: `src`) |
| `--base-url URL` | 移行元サイトのベース URL (既定: `https://computer-union.jp`) |
| `--no-download` | 画像・添付ファイルのダウンロードを行わず、Markdown のみ生成する |
| `--no-clean` | 実行前に出力先ディレクトリを削除しない |
| `--dry-run` | ファイルを書き出さず、分類結果の集計のみ表示する |
| `--limit N` | 動作確認用に、処理する記事・固定ページを先頭から N 件に制限する |

例: ネットワークに接続せずに分類結果だけ確認する場合

```sh
./venv/bin/python tools/import_wordpress.py --dry-run --no-download
```

## 3. 分類のルール

[前提と要件](../migration/01requirements.md) および実装上の判断は以下の通りです。

- WordPress の投稿 (`post`) は、カテゴリによって次のように振り分けます。
  - 「ブログ」カテゴリのみ → `src/blog/{WordPress の投稿ID}.md`
  - 「しごと情報」カテゴリのみ → `src/job/{WordPress の投稿ID}.md`
  - 「ブログ」と「しごと情報」の**両方**のカテゴリを持つ → `src/errors/{WordPress の投稿ID}.md`
    (自動振り分けできないため、手動での確認・分類が必要です。front matter に
    `wordpress_import_error` としてその旨を記載しています)
  - 上記以外のカテゴリ (または未分類) の記事 → 「トップページ以外のページ」として
    `src/pages/{WordPress の投稿ID}.md`
- WordPress の固定ページ (`page`) は、タイトルが「お問い合わせ」のものだけを
  `src/contact.md` (単一ファイル) として扱います。それ以外の固定ページは
  `src/pages/{WordPress の投稿ID}.md` に配置します。
- `attachment` / `nav_menu_item` / `wp_template` など、上記以外の投稿タイプは
  移行対象外としてスキップします。
- ブログ掲載開始より前となる WordPress の投稿 ID (`wp:post_id`) が **3500 未満**
  の記事 (`post`) ・固定ページ (`page`) は、種別やカテゴリに関わらず移行対象外としてスキップします。

## 4. 画像・添付ファイルの扱い

- 本文中の `<img>` タグが参照している画像、および `wp-content/uploads` 配下を指す
  `<a href>` (PDF・Word・Excel などの添付ファイル) を対象に、移行元サイトから
  ダウンロードします。
- **blog / job / errors** の記事内にある画像・添付ファイルは、記事と同じディレクトリに
  `{WordPress の投稿ID}_{連番3桁}.{拡張子}` という名前で配置し、本文中の参照も
  そのファイル名に書き換えます (例: `src/blog/4779_001.png`)。
- **それ以外 (pages / contact)** の画像・添付ファイルは `src/images/` の下に、
  移行元と同じファイル名で配置します。本文中の参照は `/images/{ファイル名}` に
  書き換えます。
- 同じ URL の画像・添付ファイルが複数箇所から参照されている場合、ダウンロードは
  1 回だけ行われます。
- ダウンロードに失敗したファイルがあっても処理は継続され、実行結果の最後に
  一覧が表示されます。あとで `--no-clean` を付けて再実行すると、失敗分だけ
  再ダウンロードを試みます (既にダウンロード済みのファイルは上書きされません)。

## 5. その他の変換内容

- 本文の HTML は Gutenberg のブロックコメント (`<!-- wp:... -->` など) を取り除いたうえで
  Markdown に変換しています。
- 本文中にある移行元サイトへの内部リンク (`?p=123` や `?page_id=123` 形式の旧パーマリンク)
  は、対応する記事・ページが見つかった場合、移行後のパス (`/blog/123/` など) に
  書き換えます。見つからない場合は元のリンクのまま残ります。
- 本文中にあるカテゴリアーカイブへのリンク (`?cat=N`) のうち、以下の 2 つは Hugo で
  生成される目次ページのパスに書き換えます。それ以外の `?cat=N` は元のリンクのまま
  残ります。
  - 「しごと情報」 (`?cat=5`) → `/job/`
  - 「ブログ」 (`?cat=10`) → `/blog/`
- **job** (「しごと情報」) の記事にある 2 列テーブルで、見出し行が空のもの (`|  |  |`) は
  `| 項目 | 内容 |` に置き換えます。
- 各 Markdown ファイルの front matter には、`title` / `date` / `draft` に加えて、
  `wordpress_id` (元の投稿ID) 、`wordpress_slug` (元のスラッグ)、`source_url` (元の URL) 、
  該当する場合は `categories` を出力しています。
  - `draft` は WordPress 上のステータスが `publish` 以外 (`draft` / `private` など) の
    場合に `true` になります。Hugo で下書きも含めてビルドする場合は
    `hugo --buildDrafts` を使ってください。
- お問い合わせページ本文にある Contact Form 7 のショートコード
  (`[contact-form-7 id="..." ...]`) は変換されず、そのままテキストとして残ります。
  実際のフォーム機能は別途 Hugo 側で実装する必要があります。
- 生成される URL は Hugo の既定である pretty URL (`/blog/123/` など) を前提としています。
