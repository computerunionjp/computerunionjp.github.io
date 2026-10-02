# import.ps1

$ErrorActionPreference = "Stop"

$ToolsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ToolsDir

function Get-NextId {
    param(
        [string]$ProjectDir
    )

    $names = @()

    foreach ($dir in @("blog", "job")) {
        $target = Join-Path $ProjectDir "content\$dir"

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
        return 1
    }

    return [int]$ids[0] + 1
}

function Get-Categories {
    param(
        [string]$Path
    )

    $categories = @()
    $lines = Get-Content -Path $Path -Encoding UTF8

    if ($lines.Count -eq 0 -or $lines[0].Trim() -ne "---") {
        return $categories
    }

    $inCategories = $false

    for ($i = 1; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]

        if ($line.Trim() -eq "---") {
            break
        }

        if ($line -match '^categories\s*:\s*$') {
            $inCategories = $true
            continue
        }

        if ($inCategories) {
            if ($line -match '^\s*-\s*(.+?)\s*$') {
                $value = $Matches[1].Trim("'", '"')
                $categories += $value
                continue
            }
            else {
                $inCategories = $false
            }
        }
    }

    return $categories
}

function Get-CategoryKey {
    param(
        [string[]]$Categories
    )

    if ($Categories -contains "しごと情報") {
        return "job"
    }
    if ($Categories -contains "ブログ") {
        return "blog"
    }
    return $null
}

function Import-DraftFile {
    param(
        [string]$SrcPath,
        [string]$ProjectDir,
        [bool]$Image
    )

    $categories = Get-Categories -Path $SrcPath
    $key = Get-CategoryKey -Categories $categories

    if ($null -eq $key) {
        Write-Host "$SrcPath のカテゴリを判定できません。スキップします。"
        return $null
    }

    $nextId = Get-NextId -ProjectDir $ProjectDir

    if ($key -eq "blog" -and $Image) {
        $relativePath = "content/blog/$nextId/index.md"
    }
    else {
        $relativePath = "content/$key/$nextId.md"
    }

    $destPath = Join-Path $ProjectDir ($relativePath -replace '/', [System.IO.Path]::DirectorySeparatorChar)
    $basePath = Split-Path -Parent $destPath

    if (-not (Test-Path $basePath)) {
        New-Item -ItemType Directory -Path $basePath -Force | Out-Null
    }

    Copy-Item -Path $SrcPath -Destination $destPath
    Remove-Item -Path $SrcPath

    $relSrc = Resolve-RelativePath -ProjectDir $ProjectDir -Path $SrcPath
    Write-Host "$relSrc を $relativePath としてインポートしました。"

    return $basePath
}

function Resolve-RelativePath {
    param(
        [string]$ProjectDir,
        [string]$Path
    )

    $full = [System.IO.Path]::GetFullPath($Path)
    $base = [System.IO.Path]::GetFullPath($ProjectDir)

    if (-not $base.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
        $base += [System.IO.Path]::DirectorySeparatorChar
    }

    if ($full.StartsWith($base)) {
        return $full.Substring($base.Length)
    }

    return $full
}

function Read-BlogImageChoice {
    Write-Host "ブログの記事を取り込みます。"
    Write-Host "  2. ブログ（画像無し）"
    Write-Host "  3. ブログ（画像有り）"

    while ($true) {
        $choice = (Read-Host "番号を入力してください (2～3)").Trim()

        if ($choice -eq "2") {
            return $false
        }
        if ($choice -eq "3") {
            return $true
        }

        Write-Host "2 または 3 を入力してください。"
    }
}

function Main {
    $draftsDir = Join-Path $ProjectDir "drafts"

    if (-not (Test-Path $draftsDir)) {
        Write-Host "$draftsDir が見つかりません。処理を中止します。"
        return
    }

    $entries = Get-ChildItem -Path $draftsDir -File |
        Where-Object { -not $_.Name.StartsWith(".") } |
        Sort-Object Name

    if ($entries.Count -eq 0) {
        Write-Host "drafts/ にファイルがありません。処理を中止します。"
        return
    }

    $mdFiles = $entries | Where-Object { $_.Extension -ieq ".md" }
    $otherFiles = $entries | Where-Object { $_.Extension -ine ".md" }

    if ($otherFiles.Count -gt 0) {
        if ($mdFiles.Count -eq 1) {
            $srcPath = $mdFiles[0].FullName
            $categories = Get-Categories -Path $srcPath

            if ($categories -contains "ブログ") {
                # *.md が 1 つだけで、その他のファイル（画像など）が
                # 存在し、カテゴリがブログの場合は画像有りとして取り込む。
                $basePath = Import-DraftFile -SrcPath $srcPath -ProjectDir $ProjectDir -Image $true

                if ($null -ne $basePath) {
                    foreach ($other in $otherFiles) {
                        $otherSrc = $other.FullName
                        $otherDest = Join-Path $basePath $other.Name

                        Move-Item -Path $otherSrc -Destination $otherDest

                        $relSrc = Resolve-RelativePath -ProjectDir $ProjectDir -Path $otherSrc
                        $relDest = Resolve-RelativePath -ProjectDir $ProjectDir -Path $otherDest
                        Write-Host "$relSrc を $relDest に移動しました。"
                    }
                }
                return
            }
        }

        Write-Host "drafts/ に *.md 以外のファイルが含まれているため、処理を中止します。"
        $names = ($otherFiles | ForEach-Object { $_.Name }) -join ", "
        Write-Host "対象外のファイル: $names"
        return
    }

    if ($mdFiles.Count -eq 0) {
        Write-Host "drafts/ に *.md ファイルがありません。処理を中止します。"
        return
    }

    if ($mdFiles.Count -eq 1) {
        $srcPath = $mdFiles[0].FullName
        $categories = Get-Categories -Path $srcPath

        if ($categories -contains "ブログ") {
            $image = Read-BlogImageChoice
            Import-DraftFile -SrcPath $srcPath -ProjectDir $ProjectDir -Image $image | Out-Null
            return
        }

        # ブログ以外（しごと情報など）はカテゴリに応じて自動判定する。
        Import-DraftFile -SrcPath $srcPath -ProjectDir $ProjectDir -Image $false | Out-Null
        return
    }

    # drafts/ に複数の *.md ファイルのみが存在する場合は、
    # 各ファイルのカテゴリに応じて自動的に取り込み先を決定する。
    foreach ($entry in $mdFiles) {
        $srcPath = $entry.FullName
        Import-DraftFile -SrcPath $srcPath -ProjectDir $ProjectDir -Image $false | Out-Null
    }
}

Main
