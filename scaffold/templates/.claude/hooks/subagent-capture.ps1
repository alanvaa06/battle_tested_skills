# subagent-capture.ps1 — SubagentStop hook
# Mechanically appends each finished subagent's final message (truncated) to
# docs/context/results.md, so subagent outcomes survive compaction and session
# end without spending any context tokens. The over-cap cycle in
# context-size-check.ps1 + /compact-context keeps growth bounded.
$ErrorActionPreference = 'SilentlyContinue'

$data = [Console]::In.ReadToEnd() | ConvertFrom-Json
if (-not $data) { exit 0 }

$msg = [string]$data.last_assistant_message
if (-not $msg) { exit 0 }

$root = $env:CLAUDE_PROJECT_DIR
if (-not $root) { $root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent }
$file = Join-Path $root 'docs\context\results.md'
if (-not (Test-Path $file)) { exit 0 }

# one line, ASCII-safe, capped at 200 chars
$snippet = ($msg -replace '\s+', ' ').Trim()
$snippet = -join ($snippet.ToCharArray() | ForEach-Object { if ([int]$_ -lt 128) { $_ } else { '?' } })
if ($snippet.Length -gt 200) { $snippet = $snippet.Substring(0, 200) + '...' }

$agent = if ($data.agent_type) { $data.agent_type } else { 'subagent' }
$date = Get-Date -Format 'yyyy-MM-dd'
Add-Content -Path $file -Value "- [$date] subagent ${agent}: $snippet"
exit 0
