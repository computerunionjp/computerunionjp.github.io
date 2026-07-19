# computer-union.jp

> 以下の説明ではディレクトリ（フォルダ）名の区切りに `/` （スラッシュ）を使っています。
> Windows で作業する場合は `\` （バックスラッシュ）または `¥` （半角の￥）に読み替えてください。

## 編集

`content` の下の記事の原稿を更新して GitHub に push すると自動で GitHub Actions　によりサイトに反映されます。反映には数十秒かかります。

記事の原稿には
[GitHub Flavored Markdown](https://docs.github.com/ja/get-started/writing-on-github)
の書式を使ってください。ファイルの拡張子は `*.md` です。

字句の修正程度であれば GitHub 上で直接編集することも可能ですが、使い勝手はよくありません。
[Visual Studio Code](docs/windowshowto.md) など
Markdown の編集と GitHub の操作に対応したツールの利用をお勧めします。

Python版または PowerShell版の [テンプレート挿入ツール](tools/create.md)
を使うと、適切なパスに原稿のファイルを置くことができます。

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

下記のディレクトリは Hugo が使うため使用禁止です。

- public/
- resources/

## その他

[移行ツール](tools/import_wordpress.md) --
WordPress からの移行のために作成したツールです。記録のために残しますが、運用開始後は不要です。
