"""Find and rank entrypoints: scripts, bins, README commands, routes, main guards."""
from __future__ import annotations

import json
import re

from scanner import SourceFile

RANK = {
    "project.scripts": 100, "bin": 100, "readme_command": 90, "http_route": 80,
    "__main__": 70, "cli_framework": 60, "npm_script": 50, "main_guard": 40,
    "examples_dir": 30, "notebooks": 10,
}
README_COMMAND_RE = re.compile(r"^(python|py|pdm run|poetry run|uv run|npm|npx|pnpm|yarn|bun|uvicorn|flask|node)\b")
MAIN_GUARD_RE = re.compile(r"""^\s*if\s+__name__\s*==\s*['"]__main__['"]""")
CLI_IMPORT_RE = re.compile(r"^\s*(from|import)\s+(click|typer|argparse)\b")
# A [project.scripts] key may be bare, "quoted" or 'quoted' -- a dotted name must be quoted.
SCRIPT_KEY_RE = re.compile(
    r"""^\s*(?:"([^"]+)"|'([^']+)'|([\w.-]+))\s*=\s*['"]([^'"]+)['"]"""
)
CLI_FILE_NAMES = ("cli.py", "main.py", "__main__.py")
PY_ROUTE_RE = re.compile(r"@(app|router|api|bp)\.(get|post|put|delete|patch|route)\(")
TS_ROUTE_RE = re.compile(r"""\b(app|router)\.(get|post|put|delete|patch)\(\s*['"]""")
NEXT_ROUTE_RE = re.compile(r"(^|/)(app/.*(page|route|layout)\.(tsx?|jsx?)|pages/api/.*\.(tsx?|jsx?))$")


def entrypoints(files: list[SourceFile]) -> list[dict]:
    out: list[dict] = []
    for f in files:
        if f.rel == "pyproject.toml":
            out.extend(_project_scripts(f))
        elif f.rel == "package.json":
            out.extend(_package_json(f))
        elif f.rel.lower() == "readme.md":
            out.extend(_readme(f))
        if f.stack == "py":
            out.extend(_py_file(f))
        elif f.stack == "ts":
            out.extend(_ts_file(f))
    # A directory is not a file and has no line 1: point at the first thing in it.
    examples = sorted(f.rel for f in files if f.rel.startswith("examples/"))
    if examples:
        out.append(_entry("examples_dir", "examples/", None, examples[0], 1))
    notebooks = sorted(f.rel for f in files if f.rel.endswith(".ipynb"))
    if notebooks:
        # The scan yields a directory's files in descending name order; name the
        # first notebook by path instead, so the evidence does not depend on that.
        out.append(_entry("notebooks", "notebooks", None, notebooks[0], 1, count=len(notebooks)))
    return sorted(out, key=lambda e: (-RANK[e["kind"]], e["kind"], e["name"]))


def _entry(kind: str, name: str, target: str | None, file: str, line: int, **extra) -> dict:
    return {"kind": kind, "name": name, "target": target, "rank": RANK[kind],
            "evidence": [{"file": file, "line": line}], **extra}


def _project_scripts(f: SourceFile) -> list[dict]:
    out, section = [], ""
    for i, line in enumerate(f.lines, 1):
        m = re.match(r"^\s*\[([^\]]+)\]", line)
        if m:
            section = m.group(1).strip()
            continue
        if section != "project.scripts":
            continue
        m = SCRIPT_KEY_RE.match(line)
        if m:
            name = m.group(1) or m.group(2) or m.group(3)
            out.append(_entry("project.scripts", name, m.group(4), f.rel, i))
    return out


def _package_json(f: SourceFile) -> list[dict]:
    try:
        data = json.loads("\n".join(f.lines))
    except json.JSONDecodeError:
        return []
    out: list[dict] = []
    bins = data.get("bin")
    if isinstance(bins, str):
        # A string `bin` is named after the package, and that name is not written
        # on the `"bin"` line -- but it may well be written on a dependency line.
        # The key itself is the only honest evidence.
        name = data.get("name") or "bin"
        out.append(_entry("bin", name, bins, f.rel, _line_of(f, '"bin"', "bin")))
        bins = None
    for name, target in (bins or {}).items():
        out.append(_entry("bin", name, target, f.rel, _line_of(f, f'"{name}"', "bin")))
    for name, cmd in (data.get("scripts") or {}).items():
        out.append(_entry("npm_script", name, cmd, f.rel, _line_of(f, f'"{name}"', "scripts")))
    return out


def _line_of(f: SourceFile, needle: str, section: str | None = None) -> int:
    """Line of `needle`, searched forward from the line that opens `section`.

    `bin` and `scripts` routinely define the same name, so the first line
    holding it anywhere in the file is the wrong evidence for one of them.
    """
    start = 0
    if section:
        start = next((i for i, line in enumerate(f.lines) if f'"{section}"' in line), 0)
    for i, line in enumerate(f.lines[start:], start + 1):
        if needle in line:
            return i
    # Line 0 does not exist. The section's own line is the weakest true evidence.
    return start + 1


def _readme(f: SourceFile) -> list[dict]:
    in_fence = False
    for i, line in enumerate(f.lines, 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence and README_COMMAND_RE.match(line.strip()):
            return [_entry("readme_command", line.strip(), None, f.rel, i)]
    return []


def _py_file(f: SourceFile) -> list[dict]:
    out: list[dict] = []
    if f.rel.endswith("__main__.py"):
        out.append(_entry("__main__", f.rel, None, f.rel, 1))
    routes = 0
    first_route = 0
    guarded = False
    cli_line, cli_text = 0, ""
    for i, line in enumerate(f.lines, 1):
        if MAIN_GUARD_RE.match(line):
            guarded = True
            out.append(_entry("main_guard", f.rel, None, f.rel, i))
        if CLI_IMPORT_RE.match(line) and not cli_line:
            cli_line, cli_text = i, line.strip()
        if PY_ROUTE_RE.search(line):
            routes += 1
            first_route = first_route or i
    # Importing click proves nothing on its own: a test module imports it too.
    if cli_line and (f.rel.rsplit("/", 1)[-1] in CLI_FILE_NAMES or guarded):
        out.append(_entry("cli_framework", f.rel, cli_text, f.rel, cli_line))
    if routes:
        out.append(_entry("http_route", f.rel, None, f.rel, first_route, routes=routes))
    return out


def _ts_file(f: SourceFile) -> list[dict]:
    if NEXT_ROUTE_RE.search(f.rel):
        return [_entry("http_route", f.rel, None, f.rel, 1, routes=1)]
    routes = 0
    first_route = 0
    for i, line in enumerate(f.lines, 1):
        if TS_ROUTE_RE.search(line):
            routes += 1
            first_route = first_route or i
    return [_entry("http_route", f.rel, None, f.rel, first_route, routes=routes)] if routes else []
