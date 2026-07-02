# Claude Sonnet にお願い 02

## 3. コンテンツのインポート

[前提と要件](01requirements.md) に従って `migration/imports/WordPress.xml` をインポートするツールを作成します。
ツールは Python で作成して `tools` の下に配置してください。
`venv` を利用することにします。
必要なパッケージは `requirements.txt` に記載してください。

「ブログ」または「しごと情報」以外のカテゴリの記事がある場合は「トップページ以外のページ」として扱ってください。
「ブログ」および「しごと情報」の両方のカテゴリの記事がある場合は `src/errors` の下に配置してください。

テストのために私が `src/.gitignore` を置きました。
テストが終わったら私が削除しますので、このままにしてください。

作成したツールの利用方法を `tools/import_wordpress.md` に記載してください。

### 3.1. 追加の仕様(1)

次の目次ページを Hugo で生成する前提とします。本文中にリンクがある場合はパスを書き換えてください。

- 「しごと情報」の目次ページ https://computer-union.jp/?cat=5 --> /job/
- 「ブログ」の目次ページ https://computer-union.jp/?cat=10 --> /blog/

WordPress の投稿 ID が 3500 より古い記事は移行対象外とします。

### 3.2. 追加の仕様(2)

「しごと情報」の記事で 2列のテーブルがあり、そのテーブルの見出しが空の場合
`|  |  |` は `| 項目 | 内容 |` とします。

### 3.3 追加の仕様(3)

`tools/import_wordpress.md` に引数 `--test` を追加してください。
`--test` が指定された場合は「その他のページ」から「お問い合わせ」へのリンクは
`/contact/` ではなく `https://computer-union.jp/?page_id=4650` とします。
`--test` が指定された場合は `--base-url` に `https://computerunionjp.github.io/`
が指定されているとみなします。

`--dry-run` または `--limit` が指定された場合は `--test` も指定されているとみなします。

### 3.4. 追加の仕様(4)

リンクの open_in_new は次のようにしてください。
`/images/external_link.png` は移行元からダウンロードします。

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">
  リンクテキスト<img src="/images/external_link.png " alt="external_link" />
</a>
```

例えば

```md
[MIC：マスコミ文化情報労組会議open\_in\_new](http://www.union-net.or.jp/mic/)
```

は

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">
  リンクテキスト<img src="/images/external_link.png " alt="Open in new" />
</a>
```

とします。

リンクの folder は次のようにしてください。
`/images/outline_folder_black_24dp.png` は移行元からダウンロードします。

```md
[![Folder](/images/outline_folder_black_24dp.png) リンクテキスト](/path/to/folder/)
```

例えば

```md
### [folderしごと情報](/job/)
```

は

```html
### [![Folder](/images/outline_folder_black_24dp.png) しごと情報](/job/)
```

とします。

`src/pages/4731.md` の「しごと情報」と「ブログ」のセクションにはそれぞれの最近の5件の記事のリンクを埋め込みます。
Hugo　の仕様として可能な場合、埋め込みのためのプレースホルダーを記載してください。
