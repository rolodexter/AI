#!/usr/bin/env pwsh
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path "$root\..\..\"
python "$repo\tools\scripts\lint-frontmatter.py"
if ($LASTEXITCODE -ne 0) { exit 1 }
