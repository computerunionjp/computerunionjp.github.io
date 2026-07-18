# create.ps1

$ErrorActionPreference = "Stop"

Write-Host "記事の種類を選択してください。中止する場合は何も入力せずに Enter を押してください。"
Write-Host "  1. しごと情報"
Write-Host "  2. ブログ（画像無し）"
Write-Host "  3. ブログ（画像有り）"

$choice = Read-Host "番号を入力してください (1～3)"

$category = ""
$image = $false

switch ($choice) {
    "1" {
        Write-Host "しごと情報を選択しました。"
        $category = "job"
        $image = $false
    }
    "2" {
        Write-Host "ブログ（画像無し）を選択しました。"
        $category = "blog"
        $image = $false
    }
    "3" {
        Write-Host "ブログ（画像有り）を選択しました。"
        $category = "blog"
        $image = $true
    }
    default {
        Write-Host "無効な番号です。"
        exit
    }
}

$names = @()

$toolsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $toolsDir

foreach ($dir in @("blog", "job")) {
    $target = Join-Path $projectDir "content\$dir"

    if (-not (Test-Path $target)) {
        continue
    }

    Get-ChildItem $target | ForEach-Object {
        if ($_.PSIsContainer) {
            $names += $_.Name
        }
        else {
            $names += [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        }
    }
}

$ids = $names |
    Where-Object { $_ -match '^\d+$' } |
    Sort-Object { [int]$_ } -Descending

if ($ids.Count -eq 0) {
    $id = 1
}
else {
    $id = [int]$ids[0] + 1
}

if ($image) {
    $relativePath = Join-Path "content\$category\$id" "index.md"
}
else {
    $relativePath = "content\$category\$id.md"
}

$destPath = Join-Path $projectDir $relativePath
$tmplPath = Join-Path $toolsDir "template_$category.md"

while ($true) {

    Write-Host "$relativePath を作成します。"

    $answer = (Read-Host "実行しますか？ [Y/n]").Trim()

    if ($answer -eq "") {
        $answer = "Y"
    }

    $answer = $answer.ToUpper()

    if ($answer -eq "Y") {

        $basePath = Split-Path -Parent $destPath

        if (-not (Test-Path $basePath)) {
            New-Item -ItemType Directory -Path $basePath -Force | Out-Null
        }

        $now = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"

        $output = foreach ($line in Get-Content $tmplPath -Encoding UTF8) {
            if ($line.StartsWith("date:")) {
                "date: '$now'"
            }
            else {
                $line
            }
        }

        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)

        [System.IO.File]::WriteAllLines(
            $destPath,
            $output,
            $utf8NoBom
        )

        Write-Host "作成しました: $relativePath"
        break
    }
    elseif ($answer -eq "N") {
        Write-Host "処理を中止します。"
        break
    }
    else {
        Write-Host "Y または N を入力してください。"
    }
}
