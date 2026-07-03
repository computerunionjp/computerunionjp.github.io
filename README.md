# computer-union.jp

以下の説明ではディレクトリ（フォルダ）名の区切りに `/` （スラッシュ）を使っています。
Windows で作業する場合は `\` （バックスラッシュ）または `¥` （半角の￥）に読み替えてください。

## 編集

記事の原稿には
[GitHub Flavored Markdown](https://docs.github.com/ja/get-started/writing-on-github)
の書式を使ってください。
ファイルの拡張子は `*.md` です。

Visual Studio Code など Markdown の編集と GitHub の操作に対応したツールの利用をお勧めします。

`src` の下を更新すると自動で GitHub Actions　によりサイトに反映されます。反映には数十秒かかります。

- src/
    - blog/
        - 5848.md -- ブログの原稿(1) 画像無し
        - 7251/ -- ブログの原稿(2) 画像有り
            - index.md
            - 7251_001.png
            - 7251_002.png
    - job/
        - 8065.md -- しごと情報の原稿

Python が利用できる場合は [テンプレート挿入ツール](tools/create.md) を使ってください。

Python が利用できない場合はテンプレートをコピーして使ってください。

- `tools/template_blog.md` -- ブログ
- `tools/template_job.md` -- しごと情報

ローカルでプレビューするには `hugo` が必要です。

```bash
$ git clone https://github.com/computerunionjp/computerunionjp.git
$ cd computerunionjp
$ hugo server
 ... ...
Web Server is available at http://localhost:1313/ (bind address 127.0.0.1)
Press Ctrl+C to stop
```

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

GitHub Actions の設定は `.github/workflows/on-push.yaml`　を参照してください。

下記のディレクトリは GitHub Actions で無視する設定にしています。作業のマニュアルやコンテンツ作成のための補助的なツール等を置いてください。

- docs/
- migration/
- test/
- tools/

[移行ツールの使い方](tools/import_wordpress.md)
