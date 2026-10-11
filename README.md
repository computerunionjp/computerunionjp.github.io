# computer-union.jp

> 以下の説明ではディレクトリ（フォルダ）名の区切りに `/` （スラッシュ）を使っています。
> Windows で作業する場合は `\` （バックスラッシュ）または `¥` （半角の￥）に読み替えてください。

## 編集

`content` の下の記事の原稿を更新して GitHub に push すると自動で GitHub Actions によりサイトに反映されます。反映には数十秒かかります。

記事の原稿には
[GitHub Flavored Markdown](https://docs.github.com/ja/get-started/writing-on-github)
の書式を使ってください。ファイルの拡張子は `*.md` です。

字句の修正程度であれば GitHub 上で直接編集することも可能ですが、使い勝手はよくありません。
[Visual Studio Code](docs/windowshowto.md) など
Markdown の編集と GitHub の操作に対応したツールの利用をお勧めします。

記事の作成・取り込みを支援するツールについては、後述の「[ツール](#ツール)」を
参照してください。

- content/
  - blog/
    - mmmm.md -- ブログの原稿(1) 画像無し
    - nnnn/ -- ブログの原稿(2) 画像有り
      - index.md
      - nnnn_001.png
      - nnnn_002.png
  - job/
    - oooo.md -- しごと情報の原稿

ローカルでプレビューするには Hugo が必要です。
Hugo のインストールの手順は [公式サイト](https://gohugo.io/installation/) を参照してください。

```bash
$ git clone git@github.com:computerunionjp/computerunionjp.github.io.git
$ cd computerunionjp.github.io
$ hugo server
 ... ...
Web Server is available at http://localhost:1313/ (bind address 127.0.0.1)
Press Ctrl+C to stop
```

## ツール

記事の原稿作成を支援するツールを `tools/` に用意しています。
Pythonを使うツールは、事前に以下を実行してください。

[pyenv](https://github.com/pyenv/pyenv) を使っている場合は、`.python-version`
に記載のバージョンが自動的に使用されます。

```bash
python -m venv .venv
source .venv/bin/activate   # Windows は .venv\Scripts\activate
pip install -r requirements.txt
```

| ツール | 概要 |
| --- | --- |
| [テンプレート挿入ツール](tools/create.md) | 新規記事（「ブログ」または「しごと情報」）のひな形を `content/` に作成します。 |
| [原稿取り込みツール](tools/import.md) | `drafts/` にまとめて置いた原稿（画像添付も可）を `content/` に取り込みます。 |
| [機関紙PDF変換指示書](tools/prompt-blog.md) | 組合機関紙のPDFをAIに読み込ませ、「ブログ」記事用Markdownと画像を `drafts/` に生成させるための指示書です。 |
| [しごと情報抽出ツール](tools/pick_job_sample.md) | 引き合い一覧（`*.docx`）から案件情報を抽出し、「しごと情報」記事を生成させるためのAI向け指示文面を作成します。 |

典型的な流れは次の通りです。

1. 機関紙PDFや引き合い一覧などの原材料を元に、AIに記事のMarkdownを
   生成させる（[機関紙PDF変換指示書](tools/prompt-blog.md) /
   [しごと情報抽出ツール](tools/pick_job_sample.md)）、または
   [テンプレート挿入ツール](tools/create.md) で手動執筆用のひな形を作成する。
2. 生成・執筆したMarkdownと画像を `drafts/` に置く。
3. [原稿取り込みツール](tools/import.md) で `content/` に取り込む。
4. `content/` の変更を GitHub に push する。

## 記事のサンプル

- sample/
  - blog/
    - 5848.md -- ブログのサンプル(1) 画像無し
    - 7251/ -- ブログのサンプル(2) 画像有り
      - index.md
      - 7251_001.png
      - 7251_002.png
  - job/
    - 8065.md -- しごと情報のサンプル

## 開発

GitHub Actions の設定は `.github/workflows/on-push.yaml` を参照してください。

下記のディレクトリは GitHub Actions で無視する設定にしています。作業のマニュアルやコンテンツ作成のための補助的なツール等を置いてください。

- docs/
- migration/
- test/
- tools/

下記のディレクトリは Hugo が使うため使用禁止です。

- public/
- resources/

## その他

[移行ツール](migration/import_wordpress.md) --
WordPress からの移行のために作成したツールです。記録のために残しますが、運用開始後は不要です。

## ライセンス

`tools/` と `migration/` 以下のスクリプト・ツール類は [MIT License](LICENSE) のもとで公開しています。
