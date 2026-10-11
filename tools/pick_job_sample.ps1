# pick_job_sample.ps1

$ErrorActionPreference = "Stop"

Import-Module PSWriteOffice

$ToolsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ToolsDir
$DraftsDir = Join-Path $ProjectDir "drafts"

$Headers = @("meta", "content")
$Includes = @{}
$Excludes = @{ meta = @("情報", "開示", "禁止", "秘", "取引先") }
$Limit = 10

$DateRegex = [regex]'(?:(\d{4})/)?(\d{1,2})/(\d{1,2})'

$Prompt = @'

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


'@

function ConvertTo-HalfWidthDigits {
    param(
        [string]$Text
    )

    $sb = New-Object System.Text.StringBuilder

    foreach ($ch in $Text.ToCharArray()) {
        if ($ch -ge [char]0xFF10 -and $ch -le [char]0xFF19) {
            $digit = [int]$ch - [int][char]0xFF10
            [void]$sb.Append([string]$digit)
        }
        else {
            [void]$sb.Append($ch)
        }
    }

    return $sb.ToString()
}

function Get-DocxRows {
    param(
        [string]$Path
    )

    $rows = [System.Collections.Generic.List[object]]::new()

    try {
        $tables = Get-OfficeWordTable -Path $Path
    }
    catch {
        Write-Host "Get-DocxRows: $(Split-Path -Leaf $Path): $_" -ForegroundColor Red
        return , $rows
    }

    foreach ($table in $tables) {
        foreach ($row in $table.Rows) {
            $cells = @()
            foreach ($cell in $row.Cells) {
                $texts = @()
                foreach ($p in $cell.Paragraphs) {
                    $texts += $p.Text
                }
                $cells += ($texts -join "`n")
            }
            $rows.Add($cells)
        }
    }

    return , $rows
}

function Format-Meta {
    param(
        [string]$Meta
    )

    $result = ConvertTo-HalfWidthDigits -Text $Meta
    $result = $result -replace '／|-|−|ー', '/'
    return $result
}

function Test-RowExcludes {
    param(
        [hashtable]$Row
    )

    foreach ($key in $Excludes.Keys) {
        foreach ($value in $Excludes[$key]) {
            if ($Row[$key] -like "*$value*") {
                return $false
            }
        }
    }

    return $true
}

function Test-RowIncludes {
    param(
        [hashtable]$Row
    )

    if ($Includes.Count -eq 0) {
        return $true
    }

    foreach ($key in $Includes.Keys) {
        foreach ($value in $Includes[$key]) {
            if ($Row[$key] -like "*$value*") {
                return $true
            }
        }
    }

    return $false
}

function Get-DateAndCode {
    param(
        [string]$Meta
    )

    $stripped = $Meta.Trim()
    $match = $DateRegex.Match($stripped)

    if (-not $match.Success) {
        return $null
    }

    $now = Get-Date
    $currentYear = $now.Year
    $currentMonth = $now.Month

    $metaMonth = [int]$match.Groups[2].Value

    if ($match.Groups[1].Success) {
        $year = [int]$match.Groups[1].Value
    }
    elseif ($currentMonth -le 2 -and $metaMonth -ge 11) {
        $year = $currentYear - 1
    }
    else {
        $year = $currentYear
    }

    $month = "{0:D2}" -f $metaMonth
    $day = "{0:D2}" -f [int]$match.Groups[3].Value
    $date = "$year/$month/$day"

    $remaining = ($stripped.Substring(0, $match.Index) + $stripped.Substring($match.Index + $match.Length)).Trim()
    $codeMatches = [regex]::Matches($remaining, '\d+')
    $code = ($codeMatches | ForEach-Object { $_.Value }) -join ""

    if ([string]::IsNullOrEmpty($code)) {
        return $null
    }

    return [pscustomobject]@{ Date = $date; Code = $code }
}

function Get-JobData {
    param(
        [string[]]$Paths
    )

    $allRows = [System.Collections.Generic.List[object]]::new()
    foreach ($path in $Paths) {
        $allRows.AddRange([object[]](Get-DocxRows -Path $path))
    }

    $data = @()

    foreach ($cols in $allRows) {
        if ($cols.Count -lt $Headers.Count) {
            continue
        }

        $row = @{}
        for ($i = 0; $i -lt $Headers.Count; $i++) {
            $row[$Headers[$i]] = $cols[$i]
        }
        $row["meta"] = Format-Meta -Meta $row["meta"]

        if (-not (Test-RowIncludes -Row $row)) {
            continue
        }
        if (-not (Test-RowExcludes -Row $row)) {
            continue
        }

        $parsed = Get-DateAndCode -Meta $row["meta"]
        if ($null -eq $parsed) {
            continue
        }

        $data += [pscustomobject]@{
            Date    = $parsed.Date
            Code    = $parsed.Code
            Content = $row["content"]
        }
    }

    if ($Limit -and $data.Count -gt $Limit) {
        return $data[0..($Limit - 1)]
    }

    return $data
}

function Get-OutputFileName {
    $ts = Get-Date -Format "yyyyMMddHHmmss"
    return "prompt$ts.txt"
}

function Build-Output {
    param(
        [object[]]$Data
    )

    $items = ($Data | ForEach-Object {
        "-----`ncode: $($_.Code)`ndate: $($_.Date)`n--`n$($_.Content)`n"
    }) -join "`n"

    return "$Prompt$items`n"
}

function Main {
    $docxPaths = Get-ChildItem -Path $DraftsDir -Filter "*.docx" -File -ErrorAction SilentlyContinue |
        Sort-Object Name

    if ($null -eq $docxPaths -or $docxPaths.Count -eq 0) {
        Write-Host "$DraftsDir に *.docx が見つかりません。" -ForegroundColor Red
        exit 1
    }

    Write-Host "入力ファイル:"
    foreach ($path in $docxPaths) {
        Write-Host "  $($path.Name)"
    }

    $paths = $docxPaths | ForEach-Object { $_.FullName }
    $data = Get-JobData -Paths $paths
    Write-Host "件数: $($data.Count)"

    $outputText = Build-Output -Data $data
    $outPath = Join-Path $DraftsDir (Get-OutputFileName)

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($outPath, $outputText, $utf8NoBom)

    Write-Host "出力: $outPath"
}

Main
