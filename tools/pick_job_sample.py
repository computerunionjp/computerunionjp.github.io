"""
drafts/*.docx を入力として読み込み、AI向けの指示文面
(プロンプト + 案件情報) を drafts/prompt<yyyymmddhhmmss>.txt に出力する。
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

import docx

PROMPT = """
# 案件情報抽出の指示

Guided Links の機能があるAIの場合は Guided Links を使わずに実行してください。

## 指示1

この指示の後ろに付いている「案件情報」から、次の必須条件を満たした上で優先条件に適合する上位3件を抽出してください。

### 必須条件

- 単価（金額）が明示されていること。
- 勤務地、またはリモート可・在宅可であることが明記されていること。

### 優先する条件

1. 「地方可」「地方歓迎」「フルリモート」が明記されていること。
2. 上記の条件を満たす中で、単価（契約額）が比較的高いこと。
3. 抽出する3件同士で、職種や技術分野（例: インフラ・開発・PMO等）が重複しないように分散させること。

## 指示2

抽出した3件の案件情報をそれぞれ下記のテンプレートに従って Markdown 文書を作成してください。
出力の際は、そのままコピー＆ペーストして使用できるよう、各案件の Markdown を markdown コードブロックで囲んで出力してください。
さらに各 Markdown の直後に、対応する案件の原文を添付してください。

### 原文出力ルール

- 原文は text コードブロックで囲むこと
- 原文は案件情報から該当案件のブロック全体を転載すること
- code: から次の ----- までを完全に転載すること
- 入力文の改行・空白・記号を維持すること
- 要約・省略・整形・言い換えを行わないこと
- 不要な説明や補足を追加しないこと
- 原文は Markdown 生成結果の検証用途である
- 原文と入力文が一致する状態で出力すること

## 出力形式

案件ごとに以下の順番で出力すること。

### 案件名

```markdown
（Markdown出力結果）
```

原文:

```text
（案件情報の原文をそのまま転載）
```

----- テンプレートここから -----
---
title: "'yy/m【場所】言語・職種など：タイトル"
date: "yyyy-mm-ddThh:mm:ss"
draft: false
categories:
- しごと情報
---

|  |  |
| --- | --- |
| 契約額 | 〜nn万円 |
| 期間 | 'yy年m月〜 |
| 場所 | 場所 |

#### 必要スキル

- 必要スキル 1
- 必要スキル 2

#### 業務内容

業務内容の説明の文章

- 業務内容の箇条書き 1
- 業務内容の箇条書き 2

管理番号:code
----- テンプレートここまで -----

## テンプレート記入項目についての補足説明

### date

- hh は 18 固定とします。
- mm は、1件目の案件が 01、2件目が 02、3件目が 03 です。

### title の 'yy/m

- 開始月を記載します。
- 例:
  - '26/10
  - '26/9(即日)
  - '26/12 or '27/1

### title の 【場所】 および 表の「場所」

以下の優先順で判定して設定してください。

- 名称の正規化:
  - 駅名や細かい地名が含まれる場合は自治体名に置き換える
  - 例:
    - 品川 → 港区
    - 大崎 → 品川区
    - 大宮 → さいたま市
    - 小川町 → 千代田区
    - 曙橋 → 新宿区
    - 茅場町 → 中央区
- リモートの位置判定:
  - 週3日以上のリモートの場合は「リモート/自治体名」
  - 週2日以下のリモートや出社メインの場合は「自治体名/リモート」
  - 常駐の場合は自治体名のみ
- 地方可の付記:
  - 「地方可」「地方歓迎」が明記されている場合のみ記載する
  - 例:
    - フルリモート地方可
    - リモート/江東区 地方可

### title の 言語・職種など

- プログラミング言語
- フレームワーク
- 製品名
- クラウドサービス名
- 職種

が明示されている場合のみ記載してください。

重複除外ルール:

- タイトル本体に含まれている内容は記載しない
- 言語とフレームワークが両方ある場合はフレームワークを優先する
- Java + SpringBoot の場合は SpringBoot のみ記載する

### title の タイトル

- 元の案件名から「某」と「募集」を除外してください。

### 契約額

- 「スキル見合い」「応相談」は除外する
- 金額部分のみ記載する

例:

- 65万円
- ～60万円
- 60～80万円
- 95万円

### 期間

例:

- '26年10月〜
- '26年10月 or 11月〜
- '26年10月(即日)〜
- '26年10月〜'27年3月(延長あり)

### 必要スキル

- 必須スキルのみ記載する
- 尚可スキルは記載しない
- 文面はできる限り変更しない
- 「一人称で」など不自然な表現のみ適切に補正してよい

### 業務内容

- 原文をできるだけ尊重して記載する
- 文章と箇条書きの併用可
- 内容を追加しない
- 内容を推測しない。

## 案件情報

ここからインプットとする案件情報の原文です。
案件情報は '-----' で区切られています。

"""

DRAFTS_DIR = Path(__file__).resolve().parent.parent / "drafts"

HEADERS = ["meta", "content"]
INCLUDES: dict[str, list[str]] = {}
EXCLUDES: dict[str, list[str]] = {"meta": ["情報", "開示", "禁止", "秘", "取引先"]}
LIMIT = 10

DATE_RE = re.compile(r"(?:(\d{4})/)?(\d{1,2})/(\d{1,2})")

# 全角数字 -> 半角数字 の変換テーブル
_FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")


def docx_to_rows(path: Path) -> list[list[str]]:
    """docx 内のすべての表から、行ごとのセル文字列リストを取得する。"""
    rows: list[list[str]] = []
    try:
        document = docx.Document(str(path))
    except Exception as e:  # noqa: BLE001
        print(f"docx_to_rows: {path.name}: {e}", file=sys.stderr)
        return rows

    for table in document.tables:
        for row in table.rows:
            rows.append([cell.text for cell in row.cells])
    return rows


def normalize_meta(meta: str) -> str:
    meta = meta.translate(_FULLWIDTH_DIGITS)
    meta = re.sub(r"／|-|−|ー", "/", meta)
    return meta


def row_matches_excludes(row: dict[str, str]) -> bool:
    for key, values in EXCLUDES.items():
        if any(value in row[key] for value in values):
            return False
    return True


def row_matches_includes(row: dict[str, str]) -> bool:
    if not INCLUDES:
        return True
    return any(
        any(value in row[key] for value in values)
        for key, values in INCLUDES.items()
    )


def parse_date_and_code(meta: str) -> tuple[str, str] | None:
    stripped = meta.strip()
    match = DATE_RE.search(stripped)
    if not match:
        return None

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    meta_month = int(match.group(2))
    if match.group(1):
        year = int(match.group(1))
    elif current_month <= 2 and meta_month >= 11:
        year = current_year - 1
    else:
        year = current_year

    month = f"{meta_month:02d}"
    day = f"{int(match.group(3)):02d}"
    date = f"{year}/{month}/{day}"

    remaining = (stripped[: match.start()] + stripped[match.end() :]).strip()
    code_nums = re.findall(r"\d+", remaining)
    code = "".join(code_nums) if code_nums else None

    if not code:
        return None

    return date, code


def parse_docx_files(paths: list[Path]) -> list[dict[str, str]]:
    all_rows: list[list[str]] = []
    for path in paths:
        all_rows.extend(docx_to_rows(path))

    data: list[dict[str, str]] = []
    for cols in all_rows:
        if len(cols) < len(HEADERS):
            continue
        row = {header: cols[i] for i, header in enumerate(HEADERS)}
        row["meta"] = normalize_meta(row["meta"])

        if not row_matches_includes(row):
            continue
        if not row_matches_excludes(row):
            continue

        parsed = parse_date_and_code(row["meta"])
        if not parsed:
            continue
        date, code = parsed

        data.append({"date": date, "code": code, "content": row["content"]})

    return data[:LIMIT] if LIMIT else data


def generate_file_name() -> str:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"prompt{ts}.txt"


def build_output(data: list[dict[str, str]]) -> str:
    items = "\n".join(
        f"-----\ncode: {row['code']}\ndate: {row['date']}\n--\n{row['content']}\n"
        for row in data
    )
    return f"{PROMPT}{items}\n"


def main() -> int:
    docx_paths = sorted(DRAFTS_DIR.glob("*.docx"))
    if not docx_paths:
        print(f"{DRAFTS_DIR} に *.docx が見つかりません。", file=sys.stderr)
        return 1

    print("入力ファイル:")
    for path in docx_paths:
        print(f"  {path.name}")

    data = parse_docx_files(docx_paths)
    print(f"件数: {len(data)}")

    output_text = build_output(data)
    out_path = DRAFTS_DIR / generate_file_name()
    _ = out_path.write_text(output_text, encoding="utf-8")
    print(f"出力: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
