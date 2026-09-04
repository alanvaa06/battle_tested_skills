# Install battle_tested_skills into your Claude Code skills directory.
#
# Usage:
#   ./install.ps1                      # install to ~/.claude/skills (personal, all projects)
#   ./install.ps1 .claude\skills       # install into a project's skills dir
#   ./install.ps1 C:\custom\path       # install anywhere
#
# Any top-level folder containing a SKILL.md is treated as a skill and copied
# in (overwriting an existing copy of the same name). The 'scaffold' template
# has no SKILL.md and is skipped — see the note printed at the end.
param([string]$Dest = "$HOME\.claude\skills")

$ErrorActionPreference = "Stop"
$Src = $PSScriptRoot
New-Item -ItemType Directory -Force -Path $Dest | Out-Null

$installed = 0
Get-ChildItem -Path $Src -Directory | ForEach-Object {
    if (Test-Path (Join-Path $_.FullName "SKILL.md")) {
        $target = Join-Path $Dest $_.Name
        if (Test-Path $target) { Remove-Item -Recurse -Force $target }
        Copy-Item -Recurse $_.FullName $target
        Write-Host "installed skill: $($_.Name) -> $target"
        $installed++
    }
}

Write-Host "done. $installed skill(s) installed."
Write-Host ""
Write-Host "note: 'scaffold' is a project template, not a skill. Copy it into a project root:"
Write-Host "  Copy-Item -Recurse `"$Src\scaffold\*`" C:\path\to\your\project\"
