#!/usr/bin/env bash
# Install battle_tested_skills into your Claude Code skills directory.
#
# Usage:
#   ./install.sh                 # install to ~/.claude/skills (personal, all projects)
#   ./install.sh .claude/skills  # install into a project's skills dir
#   ./install.sh /custom/path    # install anywhere
#
# Any top-level folder containing a SKILL.md is treated as a skill and copied
# in (overwriting an existing copy of the same name). The 'scaffold' template
# has no SKILL.md and is skipped — see the note printed at the end.
set -euo pipefail

DEST="${1:-$HOME/.claude/skills}"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$DEST"

installed=0
for dir in "$SRC"/*/; do
  name="$(basename "$dir")"
  if [ -f "${dir}SKILL.md" ]; then
    rm -rf "$DEST/$name"
    cp -r "$dir" "$DEST/$name"
    echo "installed skill: $name -> $DEST/$name"
    installed=$((installed + 1))
  fi
done

echo "done. $installed skill(s) installed."
echo
echo "note: 'scaffold' is a project template, not a skill. Copy it into a project root:"
echo "  cp -r \"$SRC/scaffold/.\" /path/to/your/project/"
