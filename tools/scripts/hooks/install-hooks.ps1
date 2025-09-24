param([string]$RepoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path)
$gitHooks = Join-Path $RepoRoot ".git\hooks"
if (!(Test-Path $gitHooks)) { Write-Host "No .git/hooks directory found. Initialize git first."; exit 1 }
Copy-Item -Force (Join-Path $RepoRoot "tools\scripts\hooks\pre-commit.ps1") (Join-Path $gitHooks "pre-commit")
Write-Host "Installed pre-commit hook."
