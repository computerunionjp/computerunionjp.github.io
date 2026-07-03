# テンプレート挿入ツールの使い方

新規のページIDを採番して「ブログ」または「しごと情報」の原稿のテンプレートを
`src` の下に作成します。
日付　( 3行目の date: ) は自動で設定します。

## 1. セットアップ (初回のみ)

Python 3 の `venv` を使います。プロジェクトのルートディレクトリ (`hugo.toml`
がある場所) で実行してください。

```sh
python -m venv venv
./venv/bin/pip install -r requirements.txt
```

Mac OS のシステムの　Python を使う場合は `python` を `python3` に置き換えてください。

## 2. 実行方法

同じくプロジェクトのルートディレクトリで実行してください。

```sh
$ ./venv/bin/python tools/create.py
python tools/create.py
記事の種類を選択してください。中止する場合は何も入力せずに Enter を押してください。
  1. しごと情報
  2. ブログ（画像無し）
  3. ブログ（画像有り）
番号を入力してください (1～3): 3
ブログ（画像有り）を選択しました。
src/blog/8083/index.md を作成します。
実行しますか？ [Y/n]: y
```
