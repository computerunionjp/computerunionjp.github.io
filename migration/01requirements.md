# Claude Sonnet にお願い 01

## 1. 前提

このプロジェクトでは WordPress　で構築している Web サイトを Hugo を用いたものに移行します。
移行元の URL は <https://computer-union.jp/> です。
移行元の WordPress　のコンテンツを XML　形式でエクスポートして `migration/imports/WordPress.xml` に置きました。
このプロジェクトの作業をする環境では Python 3.14 と hugo を使うことができます。

## 2. 要件

移行元のコンテンツは 4種類です。

- ブログ
- しごと情報
- お問い合わせ
- その他のページ

移行先の URL のパスは以下のようにします。

- index.html <-- トップページ
- pages/nnnn.html <-- トップページ以外のページ
- blog/nnnn.html <-- ブログ
- job/nnnn.html <-- しごと情報
- images/* <-- 画像
- contact.html <-- お問い合わせ

これらのコンテンツの原稿はHugoのためのメタ情報を追加した Markdown 形式として、
'content' の下に URL のパスと同様のディレクトリに配置します。
例えば、`blog/nnnn.html` の原稿は `content/blog/nnnn.md` に配置します。
ファイル名の `nnnn` は WordPress の投稿 ID を表します。

「ブログ」と「しごと情報」の記事に含まれる画像は、それぞれのページと同じディレクトリに
`nnnn_mmm.jpg` のような名前で配置します。
`nnnn` はその画像を含む記事の WordPress の投稿 ID を表します。。
`mmm` は記事毎の連番です。

上記以外のその他の画像は `images/` の下に配置します。
`images/` の下の画像のファイル名は、移行元と同じファイル名とします。
