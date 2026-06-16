# Push ttmens-skills to GitHub using GITHUB_TOKEN from HERMES_HOME/.env
# Usage: powershell -NoProfile -File scripts/push_to_github.ps1 [-Branch main]

param(
    [string]$Branch = "main",
    [string]$HermesHome = $(if ($env:HERMES_HOME) { $env:HERMES_HOME } else { "D:\hermes-data" })
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$EnvFile = Join-Path $HermesHome ".env"

if (-not (Test-Path $EnvFile)) {
    Write-Error "Missing $EnvFile — set HERMES_HOME or create .env with GITHUB_TOKEN"
}

$token = $null
Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^\s*GITHUB_TOKEN\s*=\s*(.+)\s*$') {
        $token = $Matches[1].Trim().Trim('"').Trim("'")
    }
}

if (-not $token) {
    Write-Error "GITHUB_TOKEN not found in $EnvFile"
}

$remote = "https://github.com/ttmens/ttmens-skills.git"
Set-Location $RepoRoot
git remote set-url origin $remote | Out-Null

$pushUrl = "https://x-access-token:${token}@github.com/ttmens/ttmens-skills.git"
Write-Host "Pushing $Branch to $remote ..."
git push $pushUrl $Branch

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

git fetch origin $Branch 2>$null
Write-Host "OK: origin/$Branch updated."
