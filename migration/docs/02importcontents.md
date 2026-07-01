# Claude Sonnet にお願い 02

## 3. コンテンツのインポート

[前提と要件](01requirements.md) に従って `migration/imports/WordPress.xml` をインポートするツールを作成します。
ツールは Python で作成して `migration/tools` の下に配置してください。
`venv` を利用することにします。
必要なパッケージは `requirements.txt` に記載してください。

「ブログ」または「しごと情報」以外のカテゴリの記事がある場合は「トップページ以外のページ」として扱ってください。
「ブログ」および「しごと情報」の両方のカテゴリの記事がある場合は `src/errors` の下に配置してください。

テストのために私が `migration/imports/.gitignore` を置きました。
テストが終わったら私が削除しますので、このままにしてください。

作成したツールの利用方法を `00README.md` に記載してください。
