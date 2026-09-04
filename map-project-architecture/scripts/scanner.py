"""Walk a repository, read its text files, and describe it (the meta block)."""
from __future__ import annotations

import json
import os
import re
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from detectors import CODE_EXT, MCP_CONFIG_FILES, SKIP_DIRS

JSON_CONSUMED_FILES = ("package.json",) + MCP_CONFIG_FILES

MANIFESTS = ("pyproject.toml", "package.json")
NON_ROOT_SEGMENTS = frozenset({"examples", "fixtures", "tests", "test", "docs", "samples"})


@dataclass
class SourceFile:
    path: Path
    rel: str
    stack: str | None
    lines: list[str] = field(default_factory=list)


def scan(root: Path, max_files: int) -> tuple[list[SourceFile], bool]:
    files: list[SourceFile] = []
    for p in _walk(root):
        if len(files) >= max_files:
            return files, True
        text = _read(p)
        if text is None:
            continue
        rel = p.relative_to(root).as_posix()
        files.append(SourceFile(p, rel, CODE_EXT.get(p.suffix.lower()), _split_lines(text)))
    return files, False


def _walk(root: Path) -> Iterator[Path]:
    pending = [root]
    seen: set[str] = {os.path.realpath(root)}  # every directory already queued
    while pending:
        d = pending.pop()
        try:
            # reverse=True so the LIFO pop() above takes directories in ascending name order.
            entries = sorted(d.iterdir(), key=lambda e: e.name.casefold(), reverse=True)
        except OSError:
            continue
        for e in entries:
            if e.is_dir():
                if e.name in SKIP_DIRS or e.name.endswith(".egg-info"):
                    continue
                if e.is_symlink():
                    continue
                # Windows junctions are not symlinks: the realpath is what catches a cycle.
                real = os.path.realpath(e)
                if real in seen:
                    continue
                seen.add(real)
                pending.append(e)
            elif e.is_file():
                yield e


def _read(p: Path) -> str | None:
    try:
        data = p.read_bytes()
    except OSError:
        return None
    if len(data) > 2_000_000 or b"\0" in data[:1024]:
        return None
    # utf-8-sig: a BOM left in place hides the first line from every detector
    # and makes json.loads reject the file outright.
    return data.decode("utf-8-sig", errors="replace")


def _split_lines(text: str) -> list[str]:
    """Split on real line breaks only: str.splitlines() also breaks on form feeds
    and other Unicode separators, which would shift every later line number."""
    if not text:
        return []
    lines = re.split(r"\r\n|\r|\n", text)
    if lines[-1] == "" and text.endswith(("\n", "\r")):
        lines.pop()
    return lines


def meta(root: Path, files: list[SourceFile], capped: bool) -> dict:
    name: str | None = None
    version: str | None = None
    pyproject = next((f for f in files if f.rel == "pyproject.toml"), None)
    if pyproject is not None:
        name, version = _pyproject_name_version(pyproject.lines)
    package_json = next((f for f in files if f.rel == "package.json"), None)
    if package_json is not None and name is None:
        try:
            data = json.loads("\n".join(package_json.lines))
            name, version = data.get("name"), data.get("version")
        except json.JSONDecodeError:
            pass
    if version is None:
        version = _dunder_version(files)
    languages = Counter(f.stack for f in files if f.stack)
    return {
        "name": name,
        "version": version,
        "commit": _commit(root),
        "roots": _roots(files),
        "files": len(files),
        "code_files": sum(languages.values()),
        "code_lines": sum(len(f.lines) for f in files if f.stack),
        "languages": dict(sorted(languages.items())),
        "capped": capped,
    }


def _pyproject_name_version(lines: list[str]) -> tuple[str | None, str | None]:
    """Name and version from [project] (PEP 621), falling back to [tool.poetry]."""
    found: dict[str, dict[str, str]] = {"project": {}, "tool.poetry": {}}
    section = ""
    for line in lines:
        m = re.match(r"^\s*\[([^\]]+)\]", line)
        if m:
            section = m.group(1).strip()
            continue
        if section not in found:
            continue
        m = re.match(r"""^\s*(name|version)\s*=\s*['"]([^'"]+)['"]""", line)
        if m:
            found[section].setdefault(m.group(1), m.group(2))
    project, poetry = found["project"], found["tool.poetry"]
    return (
        project.get("name") or poetry.get("name"),
        project.get("version") or poetry.get("version"),
    )


def _dunder_version(files: list[SourceFile]) -> str | None:
    """The package's own version, not a vendored subpackage's: shallowest wins."""
    candidates = [f for f in files if f.stack == "py" and f.rel.endswith("__init__.py")]
    for f in sorted(candidates, key=lambda f: (f.rel.count("/"), f.rel)):
        for line in f.lines:
            m = re.match(r"""^__version__\s*=\s*['"]([^'"]+)['"]""", line)
            if m:
                return m.group(1)
    return None


def json_failures(files: list[SourceFile]) -> list[dict]:
    """Every JSON file the inventory actually parses that does not parse.
    Callers that read one config or another swallow their own failure; this is
    where the file gets named. Restricted to files this tool consumes
    (package.json, MCP config files): many JSON-named configs (tsconfig.json,
    .vscode/settings.json, ...) are JSONC and allow `//` comments, so parsing
    every *.json would flag files that were never broken to begin with."""
    out: list[dict] = []
    for f in files:
        if f.rel.rsplit("/", 1)[-1] not in JSON_CONSUMED_FILES:
            continue
        try:
            json.loads("\n".join(f.lines))
        except json.JSONDecodeError as exc:
            out.append({"kind": "json_parse_failure", "file": f.rel, "line": exc.lineno})
    return out


def _commit(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def _roots(files: list[SourceFile]) -> list[str]:
    roots: set[str] = set()
    for f in files:
        parts = f.rel.split("/")
        if parts[-1] not in MANIFESTS:
            continue
        if NON_ROOT_SEGMENTS.intersection(parts[:-1]):
            continue
        roots.add("/".join(parts[:-1]) or ".")
    return sorted(roots)
