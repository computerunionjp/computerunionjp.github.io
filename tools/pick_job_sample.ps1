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

$PromptPath = Join-Path $ToolsDir "pick_job_sample_prompt.md"
$Prompt = Get-Content -Path $PromptPath -Raw -Encoding UTF8

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
