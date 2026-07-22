# precompact-log.ps1 — PreCompact hook
# PreCompact cannot inject instructions into the compaction prompt (verified
# against docs) — so this only leaves a forensic marker in sesion-log.md:
# anything decided before this line may have been summarized away. Helps
# reconstruct where context was lost when reading the log later.
$ErrorActionPreference = 'SilentlyContinue'

$null = [Console]::In.ReadToEnd()

$root = $env:CLAUDE_PROJECT_DIR
if (-not $root) { $root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent }
$file = Join-Path $root 'docs\context\sesion-log.md'
if (-not (Test-Path $file)) { exit 0 }

$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
Add-Content -Path $file -Value "- [$stamp]: context compaction (details before this point may be summarized)"
exit 0
