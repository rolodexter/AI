param(
  [string]$Kind = "paper",
  [string]$Title = "Untitled",
  [string]$Hub = "research",
  [string]$Lanes = "agents",
  [string]$Audience = "technical"
)

$today = Get-Date -Format "yyyy-MM-dd"
$slug  = ($Title.ToLower() -replace '[^a-z0-9\- ]','' -replace ' +','-')
if ($slug -eq "") { $slug = "note" }

$dir = Join-Path $PSScriptRoot "..\..\docs\atoms"
switch ($Kind) {
  "book"   { $dir = Join-Path $dir "resources" }
  "paper"  { $dir = Join-Path $dir "resources" }
  "post"   { $dir = Join-Path $dir "resources" }
  "prompt" { $dir = Join-Path $dir "prompts" }
  "dataset"{ $dir = Join-Path $dir "datasets" }
  "snippet"{ $dir = Join-Path $dir "snippets" }
  default  { $dir = Join-Path $dir "notes" }
}

New-Item -ItemType Directory -Force -Path $dir | Out-Null
$file = Join-Path $dir "$today-$slug.md"

$content = @"
---
title: "$Title"
kind: $Kind
added: $today
hub: $Hub
lanes: [$Lanes]
audience: $Audience
tags: []
source: ""
authors: []
year: 
summary: |
  TODO
links: []
starter: false
---
# Notes
- 
"@

Set-Content -Path $file -Value $content -Encoding UTF8
Write-Host "Created $file"
