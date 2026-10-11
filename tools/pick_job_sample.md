# しごと情報抽出ツールの使い方

> 以下の説明ではディレクトリ（フォルダ）名の区切りに `/` （スラッシュ）を使っています。
> Windows で作業する場合は `\` （バックスラッシュ）または `¥` （半角の￥）に読み替えてください。

営業担当などから届く「引き合い一覧」の Word ファイル（`*.docx`）から、
「しごと情報」記事の候補となる案件を抽出し、AIに渡すための指示文面
（プロンプト）を作成します。

`drafts/*.docx` を入力として読み込み、`drafts/prompt<yyyymmddhhmmss>.txt` に
AI向けの指示文面（抽出・絞り込みのルール＋候補案件の原文）を出力します。
出力されたテキストをAIのチャットに貼り付けると、「しごと情報」記事用の
Markdown（本サイトのテンプレートに沿ったもの）を3件分、生成してもらえます。

このツールは [jobsamplepicker](https://github.com/computerunionjp/jobsamplepicker)
リポジトリで開発されているHTML版アプリ（`dist/jobsamplepicker.html`）と
同じロジックを持つPython CLI版です（分割出力機能を除く）。

## 1. 必要な環境

- Python >= 3.9
- [python-docx](https://python-docx.readthedocs.io/)（`requirements.txt` に記載）

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows の場合は `source .venv/bin/activate` の代わりに
`.venv\Scripts\activate` を実行してください。

## 2. 実行方法

1. `drafts/` に「引き合い一覧」の `*.docx` ファイルを配置します。
2. プロジェクトのルートディレクトリで実行してください。

```sh
$ python tools/pick_job_sample.py
入力ファイル:
  引き合い_20261007.docx
  引き合い_20261008.docx
件数: 10
出力: drafts/prompt20261011154923.txt
```

Mac OS のシステムの Python を使う場合は `python` を `python3` に
置き換えてください。

3. 出力された `drafts/prompt<yyyymmddhhmmss>.txt` の内容を、AIのチャット
   に貼り付けて実行してください。
4. AIが生成したMarkdownを `drafts/` に `*.md` として保存し、
   [原稿取り込みツール](import.md) で `content/job/` に取り込みます。
5. 入力に使った `*.docx` と、出力された `prompt<yyyymmddhhmmss>.txt` は
   役目を終えたら `drafts/` から削除してください
   （[原稿取り込みツール](import.md) 実行時に対象外ファイルとして検出
   された場合は、スキップしてインポートを続行するか確認されます。
   スキップした場合はインポート完了後に自動的に削除されます）。

## 3. 入力ファイル（`*.docx`）の形式

`*.docx` 内の表（テーブル）から、1行につき以下の2列を読み取ります。

1. `meta` 列：日付や管理番号などを含む列
2. `content` 列：案件情報の本文

`meta` 列から日付（`m/d` または `yyyy/m/d`）と管理番号（数字）を抽出できな
い行は対象外になります。また、`meta` 列に「情報」「開示」「禁止」「秘」
「取引先」のいずれかが含まれる行も対象外になります。

抽出された案件情報は最大10件まで（`drafts/prompt<yyyymmddhhmmss>.txt` の
出力時点）に絞り込まれます。実際にAIへ渡す指示文面の中で、この中から
条件に合う上位3件をさらに絞り込むよう指示しています。

## 4. 出力ファイルの内容

`drafts/prompt<yyyymmddhhmmss>.txt` には、以下が1つのテキストとして出力
されます。

1. 案件情報の抽出条件・優先条件の指示
2. 生成するMarkdownのテンプレートと記入ルール（契約額、期間、場所の
   正規化ルールなど）
3. 抽出された案件情報の原文（`-----` 区切り）

AI側では、この指示に従って条件に合う上位3件を選び、Markdownと原文を
セットで出力します。原文は生成結果の検証用に添付されるため、AIの出力
内容が入力データを正しく反映しているか確認できます。

## 注意事項

- `drafts/` の中身（`.gitignore` 自体を除く）は Git の管理対象外です。
- 入力・出力ファイルには案件の詳細情報が含まれる場合があるため、
  取り扱いに注意してください。
- 抽出・絞り込みのルール（除外キーワードや抽出件数の上限など）を変更
  したい場合は、`tools/pick_job_sample.py` 内の `EXCLUDES` / `INCLUDES` /
  `LIMIT` を編集してください。
