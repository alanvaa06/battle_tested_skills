# map-project-architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A personal skill, `/map-project-architecture`, that inventories a Python or TypeScript repo with a stdlib-only script and renders one evidence-backed HTML architecture page to `docs/architecture/index.html` plus an Artifact.

**Architecture:** `scripts/` holds a small package of pure functions (scanner, per-stack analyzers, detector tables, graph layering, entrypoints, infra, diff) orchestrated by `inventory.py` into one JSON. `SKILL.md` tells the model to run the script, fill `templates/architecture.html` lens by lens from the JSON only, and publish. Every JSON item carries `evidence: [{file, line}]`; a lens with no items renders its "not found" block.

**Tech Stack:** Python 3.10+ stdlib (`ast`, `re`, `json`, `pathlib`, `argparse`), pytest for the script's tests, static HTML + inline SVG for the page. No third-party runtime deps.

**Spec:** `docs/2026-09-03-map-project-architecture-design.md` in the same folder. One deliberate deviation: v1 skips directories by the `SKIP_DIRS` table only and does not read `.gitignore` (deterministic across machines with or without git).

**Skill root:** `C:\Users\alanv\.claude\skills\map-project-architecture\` (in bash: `$HOME/.claude/skills/map-project-architecture`). All paths below are relative to it. All commands run from `scripts/` unless stated.

**Windows rule:** every `print()` in the scripts is ASCII-only. Use `[ok]`, `[!]`, `->`.

---

## File structure

```
SKILL.md                          procedure the model follows (Task 15)
docs/                             spec + this plan
templates/architecture.html       fixed design, lens markers (Task 14)
scripts/
  detectors.py                    pattern tables + match_line + grep_recipes (Task 2)
  scanner.py                      walk repo, read files, meta block (Task 4)
  py_analysis.py                  project package, units, import graph, contracts via ast (Tasks 5, 6)
  graph.py                        layers by topological order, cycles, independent pairs (Task 7)
  ts_analysis.py                  source root, units, relative-import graph, interfaces (Task 8)
  matches.py                      storage/external/env/url/mcp matches over files (Task 9)
  entrypoints.py                  ranked entrypoints (Task 10)
  infra.py                        docker, compose, CI, deploy, tests, tools (Task 11)
  diff.py                         inventory-to-inventory diff + ASCII render (Task 13)
  inventory.py                    CLI: build() + main() (Task 12)
  tests/
    fixtures/py_repo/             tiny Python project (Task 3)
    fixtures/ts_repo/             tiny Next-style TS project (Task 3)
    test_*.py                     one test module per script module
```

Modules import each other by bare name (`from detectors import ...`). Tests run with `python -m pytest tests -q` from `scripts/`, which puts `scripts/` on `sys.path`.

---

### Task 0: Skill folder, git, pytest

**Files:**
- Create: `.gitignore`
- Create: `scripts/__init__.py` (empty), `scripts/tests/__init__.py` (empty)

- [ ] **Step 1: Create folders and init git**

```bash
cd "$HOME/.claude/skills/map-project-architecture" && mkdir -p scripts/tests/fixtures templates && git init -q && printf '__pycache__/\n.pytest_cache/\n*.pyc\n' > .gitignore && touch scripts/__init__.py scripts/tests/__init__.py && git add -A && git commit -qm "chore: skill skeleton with approved design" && git log --oneline
```

Expected: one commit line ending in `chore: skill skeleton with approved design`.

- [ ] **Step 2: Verify pytest is available**

```bash
python -m pytest --version
```

Expected: `pytest 8.x.x` or similar. If `No module named pytest`: `python -m pip install pytest`.

---

### Task 1: Test conventions file

**Files:**
- Create: `scripts/tests/conftest.py`

- [ ] **Step 1: Write conftest with fixture paths**

```python
"""Shared paths for the script tests."""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def py_repo() -> Path:
    return FIXTURES / "py_repo"


@pytest.fixture
def ts_repo() -> Path:
    return FIXTURES / "ts_repo"
```

- [ ] **Step 2: Commit**

```bash
git add scripts/tests/conftest.py && git commit -qm "test: shared fixture paths"
```

---

### Task 2: detectors.py

**Files:**
- Create: `scripts/detectors.py`
- Test: `scripts/tests/test_detectors.py`

- [ ] **Step 1: Write the failing tests**

```python
"""detectors: the pattern tables and the per-line matcher."""
from __future__ import annotations

from detectors import ALL_DETECTORS, ENV_READ, URL_LITERAL, grep_recipes, match_line


def test_sqlalchemy_matches_python_import() -> None:
    names = [d.name for d in match_line("import sqlalchemy", "py")]
    assert names == ["sqlalchemy"]


def test_python_detector_does_not_fire_on_ts_stack() -> None:
    assert match_line("import sqlalchemy", "ts") == []


def test_supabase_js_matches_scoped_import() -> None:
    line = "import { createClient } from '@supabase/supabase-js';"
    assert [d.name for d in match_line(line, "ts")] == ["supabase-js"]


def test_fetch_url_matches_literal_url_only() -> None:
    assert [d.name for d in match_line('fetch("https://x.io")', "ts")] == ["fetch-url"]
    assert match_line("fetch(url)", "ts") == []


def test_env_read_patterns_capture_name() -> None:
    import re

    py = re.search(ENV_READ["py"], 'token = os.environ["API_KEY"]')
    assert py is not None and "API_KEY" in py.groups()
    ts = re.search(ENV_READ["ts"], "process.env.SUPABASE_URL ?? ''")
    assert ts is not None and "SUPABASE_URL" in ts.groups()


def test_url_literal_stops_at_quote_or_paren() -> None:
    assert URL_LITERAL.findall('x = "https://api.example.com/v1"') == ["https://api.example.com/v1"]


def test_grep_recipes_lists_every_detector() -> None:
    text = grep_recipes()
    for d in ALL_DETECTORS:
        assert d.name in text
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_detectors.py -q
```

Expected: `ModuleNotFoundError: No module named 'detectors'`.

- [ ] **Step 3: Write detectors.py**

```python
"""Detection tables for map-project-architecture. The only place a pattern lives.

A Detector is applied line by line to source files of its stack. A match is
evidence; nothing here decides what the match means beyond its kind.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Detector:
    name: str
    lens: str    # "storage" | "external"
    kind: str    # sql | nosql | cache | baas | object_store | file_store | http_client | sdk
    stack: str   # "py" | "ts" | "any"
    pattern: str
    grep: str

    @property
    def regex(self) -> re.Pattern[str]:
        return re.compile(self.pattern)


SKIP_DIRS: frozenset[str] = frozenset({
    ".git", ".hg", ".svn", ".venv", "venv", "env", "node_modules", "dist", "build",
    "__pycache__", ".next", ".turbo", "coverage", ".mypy_cache", ".ruff_cache",
    ".pytest_cache", "site-packages", ".idea", ".vscode", "target", "out",
})

CODE_EXT: dict[str, str] = {
    ".py": "py",
    ".ts": "ts", ".tsx": "ts", ".js": "ts", ".jsx": "ts", ".mjs": "ts", ".cjs": "ts",
}

MAX_FILES_DEFAULT = 20000

MIGRATION_DIRS: tuple[str, ...] = ("alembic", "migrations", "prisma/migrations", "supabase/migrations")
MCP_CONFIG_FILES: tuple[str, ...] = (".mcp.json", "claude_desktop_config.json")


def _py_import(module: str) -> str:
    return rf"^\s*(from\s+{module}(\.|\s)|import\s+{module}(\.|\s|$))"


def _ts_import(spec: str) -> str:
    return rf"""(from\s+['"]{spec}|require\(\s*['"]{spec})"""


STORAGE: tuple[Detector, ...] = (
    Detector("sqlalchemy", "storage", "sql", "py", _py_import("sqlalchemy"), "rg -n '^(from|import) sqlalchemy' -g '*.py'"),
    Detector("psycopg", "storage", "sql", "py", _py_import("psycopg2?"), "rg -n '^(from|import) psycopg' -g '*.py'"),
    Detector("asyncpg", "storage", "sql", "py", _py_import("asyncpg"), "rg -n '^(from|import) asyncpg' -g '*.py'"),
    Detector("sqlite3", "storage", "sql", "py", _py_import("sqlite3"), "rg -n '^(from|import) sqlite3' -g '*.py'"),
    Detector("duckdb", "storage", "sql", "py", _py_import("duckdb"), "rg -n '^(from|import) duckdb' -g '*.py'"),
    Detector("pymongo", "storage", "nosql", "py", _py_import("(pymongo|motor)"), "rg -n '^(from|import) (pymongo|motor)' -g '*.py'"),
    Detector("redis-py", "storage", "cache", "py", _py_import("redis"), "rg -n '^(from|import) redis' -g '*.py'"),
    Detector("supabase-py", "storage", "baas", "py", _py_import("supabase"), "rg -n '^(from|import) supabase' -g '*.py'"),
    Detector("boto3", "storage", "object_store", "py", _py_import("boto3"), "rg -n '^(from|import) boto3' -g '*.py'"),
    Detector("parquet-csv-write", "storage", "file_store", "py", r"\.(write_table|to_parquet|to_csv|write_csv|to_excel)\s*\(", "rg -n 'to_parquet|write_table|to_csv|write_csv|to_excel' -g '*.py'"),
    Detector("prisma", "storage", "sql", "ts", _ts_import("@prisma/client"), "rg -n '@prisma/client'"),
    Detector("drizzle", "storage", "sql", "ts", _ts_import("drizzle-orm"), "rg -n 'drizzle-orm'"),
    Detector("pg", "storage", "sql", "ts", _ts_import("pg['\"]"), "rg -n \"from ['\\\"]pg['\\\"]\""),
    Detector("supabase-js", "storage", "baas", "ts", _ts_import("@supabase/"), "rg -n '@supabase/'"),
    Detector("mongoose", "storage", "nosql", "ts", _ts_import("mongoose"), "rg -n 'mongoose'"),
    Detector("ioredis", "storage", "cache", "ts", _ts_import("(ioredis|redis['\"])"), "rg -n \"ioredis|from ['\\\"]redis['\\\"]\""),
)

EXTERNAL: tuple[Detector, ...] = (
    Detector("requests", "external", "http_client", "py", _py_import("requests"), "rg -n '^(from|import) requests' -g '*.py'"),
    Detector("httpx", "external", "http_client", "py", _py_import("httpx"), "rg -n '^(from|import) httpx' -g '*.py'"),
    Detector("aiohttp", "external", "http_client", "py", _py_import("aiohttp"), "rg -n '^(from|import) aiohttp' -g '*.py'"),
    Detector("urllib-request", "external", "http_client", "py", _py_import(r"urllib\.request"), "rg -n 'urllib.request' -g '*.py'"),
    Detector("openai-py", "external", "sdk", "py", _py_import("openai"), "rg -n '^(from|import) openai' -g '*.py'"),
    Detector("anthropic-py", "external", "sdk", "py", _py_import("anthropic"), "rg -n '^(from|import) anthropic' -g '*.py'"),
    Detector("stripe-py", "external", "sdk", "py", _py_import("stripe"), "rg -n '^(from|import) stripe' -g '*.py'"),
    Detector("slack-py", "external", "sdk", "py", _py_import("slack_sdk"), "rg -n '^(from|import) slack_sdk' -g '*.py'"),
    Detector("google-api-py", "external", "sdk", "py", _py_import(r"(googleapiclient|google\.cloud|google\.oauth2)"), "rg -n 'googleapiclient|google.cloud|google.oauth2' -g '*.py'"),
    Detector("twilio-py", "external", "sdk", "py", _py_import("twilio"), "rg -n '^(from|import) twilio' -g '*.py'"),
    Detector("axios", "external", "http_client", "ts", _ts_import("axios"), "rg -n \"from ['\\\"]axios\""),
    Detector("ky", "external", "http_client", "ts", _ts_import("ky['\"]"), "rg -n \"from ['\\\"]ky['\\\"]\""),
    Detector("node-fetch", "external", "http_client", "ts", _ts_import("node-fetch"), "rg -n 'node-fetch'"),
    Detector("fetch-url", "external", "http_client", "ts", r"""\bfetch\(\s*['"`]https?://""", "rg -n \"fetch\\(\\s*['\\\"\\`]https?://\""),
    Detector("openai-js", "external", "sdk", "ts", _ts_import("openai"), "rg -n \"from ['\\\"]openai\""),
    Detector("anthropic-js", "external", "sdk", "ts", _ts_import("@anthropic-ai/"), "rg -n '@anthropic-ai/'"),
    Detector("stripe-js", "external", "sdk", "ts", _ts_import("stripe"), "rg -n \"from ['\\\"]stripe\""),
    Detector("slack-js", "external", "sdk", "ts", _ts_import("@slack/"), "rg -n '@slack/'"),
    Detector("googleapis-js", "external", "sdk", "ts", _ts_import("googleapis"), "rg -n 'googleapis'"),
    Detector("resend-js", "external", "sdk", "ts", _ts_import("resend"), "rg -n \"from ['\\\"]resend\""),
)

ALL_DETECTORS: tuple[Detector, ...] = STORAGE + EXTERNAL

ENV_READ: dict[str, str] = {
    "py": r"""os\.environ(?:\.get)?\s*[\[\(]\s*['"]([A-Z][A-Z0-9_]*)['"]|os\.getenv\(\s*['"]([A-Z][A-Z0-9_]*)['"]""",
    "ts": r"""process\.env\.([A-Z][A-Z0-9_]*)|process\.env\[['"]([A-Z][A-Z0-9_]*)['"]\]""",
}

URL_LITERAL: re.Pattern[str] = re.compile(r"""['"`](https?://[^'"`\s)]+)""")


def match_line(line: str, stack: str) -> list[Detector]:
    """Every detector of this stack (or 'any') whose pattern hits the line."""
    return [d for d in ALL_DETECTORS if d.stack in (stack, "any") and d.regex.search(line)]


def grep_recipes() -> str:
    """Markdown table of manual recipes: the fallback when the script cannot run."""
    rows = ["| lens | detector | kind | stack | grep |", "|---|---|---|---|---|"]
    for d in ALL_DETECTORS:
        rows.append(f"| {d.lens} | {d.name} | {d.kind} | {d.stack} | `{d.grep}` |")
    return "\n".join(rows)
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_detectors.py -q
```

Expected: `7 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/detectors.py scripts/tests/test_detectors.py && git commit -qm "feat: detector tables and per-line matcher"
```

---

### Task 3: Fixture repos

Two tiny repos the rest of the tests run against. Create every file exactly.

**Files:** all under `scripts/tests/fixtures/`.

- [ ] **Step 1: Create py_repo**

`py_repo/pyproject.toml`
```toml
[project]
name = "demo"
version = "0.1.0"

[project.scripts]
demo = "demo.cli:main"

[tool.ruff]
line-length = 100
```

`py_repo/README.md`
````markdown
# demo

Run it:

```bash
python -m demo
```
````

`py_repo/Dockerfile`
```dockerfile
FROM python:3.12-slim
COPY . /app
```

`py_repo/.github/workflows/ci.yml`
```yaml
name: CI
on:
  push:
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
```

`py_repo/alembic/env.py`
```python
# alembic env
```

`py_repo/tests/test_demo.py`
```python
def test_ok() -> None:
    assert True
```

`py_repo/node_modules/skipme/index.js`
```js
const pg = require('pg');
```

`py_repo/src/demo/__init__.py`
```python
"""demo."""
```

`py_repo/src/demo/core/__init__.py` (empty file)

`py_repo/src/demo/core/base.py`
```python
from abc import ABC, abstractmethod


class Repo(ABC):
    @abstractmethod
    def get(self, key: str) -> str: ...
```

`py_repo/src/demo/db/__init__.py` (empty file)

`py_repo/src/demo/db/pg.py`
```python
import sqlalchemy

from demo.core.base import Repo


class PgRepo(Repo):
    def get(self, key: str) -> str:
        return str(sqlalchemy.__version__) + key
```

`py_repo/src/demo/api/__init__.py` (empty file)

`py_repo/src/demo/api/client.py`
```python
import os

import requests

BASE = "https://api.example.com/v1"


def fetch() -> str:
    token = os.environ["API_KEY"]
    return requests.get(BASE, headers={"Authorization": token}).text
```

`py_repo/src/demo/cli.py`
```python
import click

from .api.client import fetch
from demo.db.pg import PgRepo


@click.command()
def main() -> None:
    click.echo(fetch() + PgRepo().get("x"))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create ts_repo**

`ts_repo/package.json`
```json
{
  "name": "tsdemo",
  "version": "1.2.0",
  "bin": { "tsdemo": "./dist/cli.js" },
  "scripts": { "dev": "next dev", "build": "next build" },
  "dependencies": { "@supabase/supabase-js": "^2.0.0", "axios": "^1.0.0" },
  "devDependencies": { "typescript": "^5.0.0", "vitest": "^1.0.0" }
}
```

`ts_repo/vercel.json`
```json
{}
```

`ts_repo/src/lib/db.ts`
```ts
import { createClient } from '@supabase/supabase-js';

export const db = createClient(process.env.SUPABASE_URL ?? '', process.env.SUPABASE_KEY ?? '');
```

`ts_repo/src/lib/types.ts`
```ts
export interface Store {
  get(id: string): Promise<string>;
  put(id: string, value: string): Promise<void>;
}
```

`ts_repo/src/services/user.ts`
```ts
import axios from 'axios';
import { db } from '../lib/db';
import type { Store } from '../lib/types';

export async function getUser(id: string): Promise<string> {
  const res = await fetch("https://api.example.com/users/" + id);
  void axios; void db;
  return res.text();
}

export class MemoryStore implements Store {
  async get(id: string): Promise<string> { return id; }
  async put(): Promise<void> {}
}
```

`ts_repo/src/app/api/users/route.ts`
```ts
import { getUser } from '../../../services/user';

export async function GET(): Promise<Response> {
  return new Response(await getUser('1'));
}
```

- [ ] **Step 3: Verify the tree**

```bash
find tests/fixtures -type f | sort
```

Expected: 22 paths, including `tests/fixtures/py_repo/node_modules/skipme/index.js` and `tests/fixtures/ts_repo/src/app/api/users/route.ts`.

- [ ] **Step 4: Commit**

```bash
git add -f scripts/tests/fixtures && git commit -qm "test: py_repo and ts_repo fixtures"
```

(`-f` because `node_modules` inside the fixture must be tracked.)

---

### Task 4: scanner.py (walk + meta)

**Files:**
- Create: `scripts/scanner.py`
- Test: `scripts/tests/test_scanner.py`

- [ ] **Step 1: Write the failing tests**

```python
"""scanner: walk the repo, read text files, build the meta block."""
from __future__ import annotations

from pathlib import Path

from scanner import meta, scan


def test_scan_skips_node_modules_and_reads_lines(py_repo: Path) -> None:
    files, capped = scan(py_repo, max_files=1000)
    rels = {f.rel for f in files}
    assert "src/demo/cli.py" in rels
    assert not any(r.startswith("node_modules/") for r in rels)
    assert capped is False
    cli = next(f for f in files if f.rel == "src/demo/cli.py")
    assert cli.stack == "py"
    assert cli.lines[0] == "import click"


def test_scan_caps_file_count(py_repo: Path) -> None:
    files, capped = scan(py_repo, max_files=3)
    assert len(files) == 3 and capped is True


def test_meta_reads_pyproject(py_repo: Path) -> None:
    files, capped = scan(py_repo, max_files=1000)
    m = meta(py_repo, files, capped)
    assert m["name"] == "demo" and m["version"] == "0.1.0"
    assert m["roots"] == ["."]
    assert m["languages"] == {"py": 7}
    assert m["capped"] is False


def test_meta_reads_package_json(ts_repo: Path) -> None:
    files, capped = scan(ts_repo, max_files=1000)
    m = meta(ts_repo, files, capped)
    assert m["name"] == "tsdemo" and m["version"] == "1.2.0"
    assert m["languages"] == {"ts": 4}
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_scanner.py -q
```

Expected: `ModuleNotFoundError: No module named 'scanner'`.

- [ ] **Step 3: Write scanner.py**

```python
"""Walk a repository, read its text files, and describe it (the meta block)."""
from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from detectors import CODE_EXT, SKIP_DIRS

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
        files.append(SourceFile(p, rel, CODE_EXT.get(p.suffix.lower()), text.splitlines()))
    return files, False


def _walk(root: Path) -> Iterator[Path]:
    pending = [root]
    while pending:
        d = pending.pop()
        try:
            entries = sorted(d.iterdir(), reverse=True)
        except OSError:
            continue
        for e in entries:
            if e.is_dir():
                if e.name in SKIP_DIRS or e.name.endswith(".egg-info"):
                    continue
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
    return data.decode("utf-8", errors="replace")


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
    section = ""
    name = version = None
    for line in lines:
        m = re.match(r"^\s*\[([^\]]+)\]", line)
        if m:
            section = m.group(1).strip()
            continue
        if section != "project":
            continue
        m = re.match(r"""^\s*(name|version)\s*=\s*['"]([^'"]+)['"]""", line)
        if m:
            if m.group(1) == "name":
                name = m.group(2)
            else:
                version = m.group(2)
    return name, version


def _dunder_version(files: list[SourceFile]) -> str | None:
    for f in files:
        if f.stack != "py" or not f.rel.endswith("__init__.py"):
            continue
        for line in f.lines:
            m = re.match(r"""^__version__\s*=\s*['"]([^'"]+)['"]""", line)
            if m:
                return m.group(1)
    return None


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
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_scanner.py -q
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/scanner.py scripts/tests/test_scanner.py && git commit -qm "feat: repo scanner and meta block"
```

---

### Task 5: py_analysis.py (project package, units, import graph)

**Files:**
- Create: `scripts/py_analysis.py`
- Test: `scripts/tests/test_py_analysis.py`

- [ ] **Step 1: Write the failing tests**

```python
"""py_analysis: package discovery, units, import graph, contracts (ast-based)."""
from __future__ import annotations

from pathlib import Path

import pytest

from py_analysis import contracts, import_graph, project_package, units
from scanner import scan


@pytest.fixture
def py_files(py_repo: Path):
    files, _ = scan(py_repo, max_files=1000)
    return files


def test_project_package_is_the_one_with_children(py_files) -> None:
    assert project_package(py_files) == ("src/demo", "demo")


def test_units_are_child_packages_and_modules(py_files) -> None:
    u = units(py_files, "src/demo")
    assert sorted(u) == ["api", "cli", "core", "db"]
    assert u["core"]["files"] == 2 and u["cli"]["files"] == 1
    assert u["core"]["kind"] == "package" and u["cli"]["kind"] == "module"


def test_import_graph_resolves_absolute_and_relative(py_files) -> None:
    g = import_graph(py_files, "src/demo", "demo")
    edges = {(e["from"], e["to"]): e["count"] for e in g["edges"]}
    assert edges == {("db", "core"): 1, ("cli", "api"): 1, ("cli", "db"): 1}
    assert g["parse_failures"] == []
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_py_analysis.py -q
```

Expected: `ModuleNotFoundError: No module named 'py_analysis'`.

- [ ] **Step 3: Write py_analysis.py (graph half)**

```python
"""Python analysis via ast: project package, units, import graph, contracts."""
from __future__ import annotations

import ast
import posixpath
from collections import Counter

from scanner import SourceFile


def _dirname(rel: str) -> str:
    return posixpath.dirname(rel)


def _module_path(dir_rel: str) -> str:
    parts = dir_rel.split("/")
    if parts and parts[0] == "src":
        parts = parts[1:]
    return ".".join(parts)


def project_package(files: list[SourceFile]) -> tuple[str, str] | None:
    """(dir, module) of the shallowest package with >= 2 child packages, else the shallowest package."""
    pkg_dirs = sorted(
        {_dirname(f.rel) for f in files if f.rel.endswith("__init__.py") and "/" in f.rel},
        key=lambda d: (d.count("/"), d),
    )
    if not pkg_dirs:
        return None
    for d in pkg_dirs:
        children = [c for c in pkg_dirs if _dirname(c) == d]
        if len(children) >= 2:
            return d, _module_path(d)
    return pkg_dirs[0], _module_path(pkg_dirs[0])


def unit_of(rel: str, pkg_dir: str) -> str | None:
    """First segment under the project package; None for files outside it or its __init__."""
    prefix = pkg_dir + "/"
    if not rel.startswith(prefix):
        return None
    rest = rel[len(prefix):]
    if "/" in rest:
        return rest.split("/", 1)[0]
    if rest == "__init__.py":
        return None
    return rest[:-3] if rest.endswith(".py") else rest


def units(files: list[SourceFile], pkg_dir: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for f in files:
        if f.stack != "py":
            continue
        u = unit_of(f.rel, pkg_dir)
        if u is None:
            continue
        kind = "package" if "/" in f.rel[len(pkg_dir) + 1:] else "module"
        entry = out.setdefault(u, {"name": u, "kind": kind, "files": 0, "lines": 0})
        entry["files"] += 1
        entry["lines"] += len(f.lines)
    return out


def _file_module(rel: str, pkg_dir: str, pkg_module: str) -> tuple[str, bool]:
    rest = rel[len(pkg_dir) + 1:]
    is_init = rest.endswith("__init__.py")
    rest = rest[: -len("/__init__.py")] if is_init and "/" in rest else rest
    if rest == "__init__.py":
        return pkg_module, True
    rest = rest[:-3] if rest.endswith(".py") else rest
    return pkg_module + "." + rest.replace("/", "."), is_init


def _resolve_from(node: ast.ImportFrom, module: str, is_init: bool) -> list[str]:
    if node.level == 0:
        base = node.module or ""
    else:
        pkg = module if is_init else module.rsplit(".", 1)[0]
        for _ in range(node.level - 1):
            pkg = pkg.rsplit(".", 1)[0] if "." in pkg else ""
        base = pkg + ("." + node.module if node.module else "")
    if node.module is None:
        return [f"{base}.{alias.name}" for alias in node.names]
    return [base]


def import_graph(files: list[SourceFile], pkg_dir: str, pkg_module: str) -> dict:
    edges: Counter[tuple[str, str]] = Counter()
    failures: list[dict] = []
    for f in files:
        if f.stack != "py":
            continue
        src = unit_of(f.rel, pkg_dir)
        if src is None:
            continue
        module, is_init = _file_module(f.rel, pkg_dir, pkg_module)
        try:
            tree = ast.parse("\n".join(f.lines))
        except SyntaxError as exc:
            failures.append({"file": f.rel, "line": exc.lineno or 0})
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = _resolve_from(node, module, is_init)
            else:
                continue
            for name in names:
                if name != pkg_module and not name.startswith(pkg_module + "."):
                    continue
                rest = name[len(pkg_module) + 1:]
                dst = rest.split(".", 1)[0] if rest else None
                if dst and dst != src:
                    edges[(src, dst)] += 1
    return {
        "edges": [{"from": a, "to": b, "count": n} for (a, b), n in sorted(edges.items())],
        "parse_failures": failures,
    }


def contracts(files: list[SourceFile], pkg_dir: str) -> list[dict]:
    raise NotImplementedError  # Task 6
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_py_analysis.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/py_analysis.py scripts/tests/test_py_analysis.py && git commit -qm "feat: python units and import graph via ast"
```

---

### Task 6: py_analysis.py (contracts)

**Files:**
- Modify: `scripts/py_analysis.py` (replace the `contracts` stub)
- Test: `scripts/tests/test_py_analysis.py` (append)

- [ ] **Step 1: Append the failing test**

```python
def test_contracts_find_abc_and_implementers(py_files) -> None:
    cs = contracts(py_files, "src/demo")
    assert len(cs) == 1
    c = cs[0]
    assert c["name"] == "Repo" and c["kind"] == "abc" and c["unit"] == "core"
    assert c["abstract_methods"] == ["get"]
    assert c["implementers"] == [{"name": "PgRepo", "unit": "db", "file": "src/demo/db/pg.py", "line": 6}]
    assert c["evidence"] == [{"file": "src/demo/core/base.py", "line": 4}]
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_py_analysis.py::test_contracts_find_abc_and_implementers -q
```

Expected: `NotImplementedError`.

- [ ] **Step 3: Replace the contracts stub**

```python
def _base_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Subscript):
        return _base_name(node.value)
    return ""


def _decorator_name(node: ast.expr) -> str:
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return _base_name(node)


def contracts(files: list[SourceFile], pkg_dir: str) -> list[dict]:
    classes: list[dict] = []
    for f in files:
        if f.stack != "py":
            continue
        unit = unit_of(f.rel, pkg_dir)
        if unit is None:
            continue
        try:
            tree = ast.parse("\n".join(f.lines))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            bases = [_base_name(b) for b in node.bases]
            metaclass = any(
                kw.arg == "metaclass" and _base_name(kw.value) == "ABCMeta" for kw in node.keywords
            )
            abstract = [
                m.name for m in node.body
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                and any(_decorator_name(d) == "abstractmethod" for d in m.decorator_list)
            ]
            kind = "protocol" if "Protocol" in bases else "abc" if ("ABC" in bases or metaclass or abstract) else None
            classes.append({
                "name": node.name, "bases": bases, "unit": unit, "file": f.rel,
                "line": node.lineno, "abstract_methods": abstract, "kind": kind,
            })
    out: list[dict] = []
    for c in classes:
        if c["kind"] is None:
            continue
        implementers = [
            {"name": o["name"], "unit": o["unit"], "file": o["file"], "line": o["line"]}
            for o in classes if c["name"] in o["bases"]
        ]
        out.append({
            "name": c["name"], "kind": c["kind"], "unit": c["unit"],
            "abstract_methods": c["abstract_methods"],
            "implementers": sorted(implementers, key=lambda i: (i["unit"], i["name"])),
            "evidence": [{"file": c["file"], "line": c["line"]}],
        })
    return sorted(out, key=lambda c: (c["unit"], c["name"]))
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_py_analysis.py -q
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/py_analysis.py scripts/tests/test_py_analysis.py && git commit -qm "feat: python contracts (ABC, Protocol) with implementers"
```

---

### Task 7: graph.py (layers, cycles, independent pairs)

**Files:**
- Create: `scripts/graph.py`
- Test: `scripts/tests/test_graph.py`

- [ ] **Step 1: Write the failing tests**

```python
"""graph: layer units by import direction; report cycles and independent pairs."""
from __future__ import annotations

from graph import layers


def _edges(pairs):
    return [{"from": a, "to": b, "count": 1} for a, b in pairs]


def test_layers_bottom_up_and_independent_pairs() -> None:
    result = layers(["api", "cli", "core", "db"], _edges([("db", "core"), ("cli", "api"), ("cli", "db")]))
    assert result["layers"] == [["api", "core"], ["db"], ["cli"]]
    assert result["cycles"] == []
    assert result["independent_pairs"] == [["api", "core"]]


def test_cycle_is_reported_and_layered_together() -> None:
    result = layers(["a", "b", "c"], _edges([("a", "b"), ("b", "a"), ("c", "a")]))
    assert result["cycles"] == [["a", "b"]]
    assert result["layers"] == [["a", "b"], ["c"]]


def test_isolated_units_land_in_layer_zero() -> None:
    result = layers(["x", "y"], [])
    assert result["layers"] == [["x", "y"]]
    assert result["independent_pairs"] == [["x", "y"]]
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_graph.py -q
```

Expected: `ModuleNotFoundError: No module named 'graph'`.

- [ ] **Step 3: Write graph.py**

```python
"""Layer a package graph by import direction (Tarjan SCC + longest path)."""
from __future__ import annotations

from itertools import combinations


def _tarjan(deps: dict[str, set[str]]) -> list[list[str]]:
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    sccs: list[list[str]] = []
    counter = 0

    def strong(v: str) -> None:
        nonlocal counter
        index[v] = low[v] = counter
        counter += 1
        stack.append(v)
        on_stack.add(v)
        for w in sorted(deps[v]):
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp: list[str] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                comp.append(w)
                if w == v:
                    break
            sccs.append(sorted(comp))

    for v in sorted(deps):
        if v not in index:
            strong(v)
    return sccs


def layers(units: list[str], edges: list[dict]) -> dict:
    deps: dict[str, set[str]] = {u: set() for u in units}
    for e in edges:
        if e["from"] in deps and e["to"] in deps:
            deps[e["from"]].add(e["to"])
    sccs = _tarjan(deps)
    comp = {u: i for i, c in enumerate(sccs) for u in c}
    cdeps: dict[int, set[int]] = {i: set() for i in range(len(sccs))}
    for u, ds in deps.items():
        for d in ds:
            if comp[u] != comp[d]:
                cdeps[comp[u]].add(comp[d])
    level: dict[int, int] = {}

    def lv(i: int) -> int:
        if i not in level:
            level[i] = 0 if not cdeps[i] else 1 + max(lv(j) for j in cdeps[i])
        return level[i]

    unit_level = {u: lv(comp[u]) for u in units}
    depth = max(unit_level.values(), default=-1) + 1
    layer_lists = [sorted(u for u, l in unit_level.items() if l == k) for k in range(depth)]
    edge_set = {(e["from"], e["to"]) for e in edges}
    independent = [
        [a, b] for layer in layer_lists for a, b in combinations(layer, 2)
        if (a, b) not in edge_set and (b, a) not in edge_set
    ]
    return {
        "layers": layer_lists,
        "cycles": [c for c in sccs if len(c) > 1],
        "independent_pairs": independent,
    }
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_graph.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/graph.py scripts/tests/test_graph.py && git commit -qm "feat: import layers, cycles and independent pairs"
```

---

### Task 8: ts_analysis.py

**Files:**
- Create: `scripts/ts_analysis.py`
- Test: `scripts/tests/test_ts_analysis.py`

- [ ] **Step 1: Write the failing tests**

```python
"""ts_analysis: source root, units, relative-import graph, interfaces."""
from __future__ import annotations

from pathlib import Path

import pytest

from scanner import scan
from ts_analysis import contracts, import_graph, source_root, units


@pytest.fixture
def ts_files(ts_repo: Path):
    files, _ = scan(ts_repo, max_files=1000)
    return files


def test_source_root_is_src(ts_files) -> None:
    assert source_root(ts_files) == "src"


def test_units_are_first_dirs_under_root(ts_files) -> None:
    u = units(ts_files, "src")
    assert sorted(u) == ["app", "lib", "services"]
    assert u["lib"]["files"] == 2


def test_import_graph_resolves_relative_only(ts_files) -> None:
    g = import_graph(ts_files, "src")
    edges = {(e["from"], e["to"]): e["count"] for e in g["edges"]}
    assert edges == {("services", "lib"): 2, ("app", "services"): 1}
    assert g["unresolved"] == []


def test_alias_imports_are_reported_unresolved(ts_repo: Path, tmp_path: Path) -> None:
    (tmp_path / "src" / "a").mkdir(parents=True)
    (tmp_path / "src" / "a" / "x.ts").write_text("import { y } from '@/b/y';\n", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=100)
    g = import_graph(files, "src")
    assert g["edges"] == []
    assert g["unresolved"] == [{"file": "src/a/x.ts", "line": 1, "spec": "@/b/y"}]


def test_contracts_find_interface_and_implementers(ts_files) -> None:
    cs = contracts(ts_files, "src")
    assert len(cs) == 1
    c = cs[0]
    assert c["name"] == "Store" and c["kind"] == "interface" and c["unit"] == "lib"
    assert c["abstract_methods"] == ["get", "put"]
    assert c["implementers"] == [{"name": "MemoryStore", "unit": "services", "file": "src/services/user.ts", "line": 11}]
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_ts_analysis.py -q
```

Expected: `ModuleNotFoundError: No module named 'ts_analysis'`.

- [ ] **Step 3: Write ts_analysis.py**

```python
"""TypeScript/JS analysis by regex: source root, units, relative imports, interfaces."""
from __future__ import annotations

import posixpath
import re
from collections import Counter

from scanner import SourceFile

SOURCE_ROOTS = ("src", "app", "lib", "packages")
IMPORT_RE = re.compile(
    r"""(?:import|export)\s+(?:[^'";]*?\s+from\s+)?['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]\s*\)"""
)
ALIAS_PREFIXES = ("@/", "~/", "#", "$")
INTERFACE_RE = re.compile(r"^\s*export\s+(?:declare\s+)?interface\s+(\w+)")
ABSTRACT_CLASS_RE = re.compile(r"^\s*export\s+(?:declare\s+)?abstract\s+class\s+(\w+)")
ABSTRACT_MEMBER_RE = re.compile(r"^\s*(?:public\s+|protected\s+)?abstract\s+(\w+)\s*[(<:]")
MEMBER_RE = re.compile(r"^\s*(?:readonly\s+)?(\w+)\s*[(?:<]")
CLASS_RE = re.compile(r"\bclass\s+(\w+)[^{]*?\b(?:implements|extends)\s+([\w\s,<>]+)")


def source_root(files: list[SourceFile]) -> str:
    dirs = {f.rel.split("/", 1)[0] for f in files if f.stack == "ts" and "/" in f.rel}
    for candidate in SOURCE_ROOTS:
        if candidate in dirs:
            return candidate
    return ""


def unit_of(rel: str, root: str) -> str | None:
    prefix = root + "/" if root else ""
    if not rel.startswith(prefix):
        return None
    rest = rel[len(prefix):]
    if "/" in rest:
        return rest.split("/", 1)[0]
    return posixpath.splitext(rest)[0]


def units(files: list[SourceFile], root: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for f in files:
        if f.stack != "ts":
            continue
        u = unit_of(f.rel, root)
        if u is None:
            continue
        rest = f.rel[len(root) + 1:] if root else f.rel
        kind = "package" if "/" in rest else "module"
        entry = out.setdefault(u, {"name": u, "kind": kind, "files": 0, "lines": 0})
        entry["files"] += 1
        entry["lines"] += len(f.lines)
    return out


def import_graph(files: list[SourceFile], root: str) -> dict:
    edges: Counter[tuple[str, str]] = Counter()
    unresolved: list[dict] = []
    for f in files:
        if f.stack != "ts":
            continue
        src = unit_of(f.rel, root)
        if src is None:
            continue
        for line_no, line in enumerate(f.lines, 1):
            for m in IMPORT_RE.finditer(line):
                spec = m.group(1) or m.group(2)
                if spec.startswith("."):
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(f.rel), spec))
                    dst = unit_of(target, root)
                    if dst and dst != src:
                        edges[(src, dst)] += 1
                elif spec.startswith(ALIAS_PREFIXES):
                    unresolved.append({"file": f.rel, "line": line_no, "spec": spec})
    return {
        "edges": [{"from": a, "to": b, "count": n} for (a, b), n in sorted(edges.items())],
        "unresolved": unresolved,
    }


def _members(lines: list[str], start: int, abstract_only: bool) -> list[str]:
    names: list[str] = []
    for line in lines[start:]:
        if line.startswith("}"):
            break
        m = (ABSTRACT_MEMBER_RE if abstract_only else MEMBER_RE).match(line)
        if m:
            names.append(m.group(1))
    return names


def contracts(files: list[SourceFile], root: str) -> list[dict]:
    declared: list[dict] = []
    implementers: list[dict] = []
    for f in files:
        if f.stack != "ts":
            continue
        unit = unit_of(f.rel, root)
        if unit is None:
            continue
        for i, line in enumerate(f.lines):
            m = INTERFACE_RE.match(line)
            if m:
                declared.append({"name": m.group(1), "kind": "interface", "unit": unit, "file": f.rel,
                                 "line": i + 1, "abstract_methods": _members(f.lines, i + 1, False)})
                continue
            m = ABSTRACT_CLASS_RE.match(line)
            if m:
                declared.append({"name": m.group(1), "kind": "abstract_class", "unit": unit, "file": f.rel,
                                 "line": i + 1, "abstract_methods": _members(f.lines, i + 1, True)})
                continue
            m = CLASS_RE.search(line)
            if m:
                targets = [t.strip().split("<")[0] for t in m.group(2).split(",")]
                implementers.append({"name": m.group(1), "unit": unit, "file": f.rel, "line": i + 1, "targets": targets})
    out: list[dict] = []
    for d in declared:
        impl = [
            {"name": i["name"], "unit": i["unit"], "file": i["file"], "line": i["line"]}
            for i in implementers if d["name"] in i["targets"]
        ]
        out.append({
            "name": d["name"], "kind": d["kind"], "unit": d["unit"],
            "abstract_methods": d["abstract_methods"],
            "implementers": sorted(impl, key=lambda i: (i["unit"], i["name"])),
            "evidence": [{"file": d["file"], "line": d["line"]}],
        })
    return sorted(out, key=lambda c: (c["unit"], c["name"]))
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_ts_analysis.py -q
```

Expected: `5 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/ts_analysis.py scripts/tests/test_ts_analysis.py && git commit -qm "feat: typescript units, relative-import graph and interfaces"
```

---

### Task 9: matches.py (storage, external, env, urls, migrations, mcp)

**Files:**
- Create: `scripts/matches.py`
- Test: `scripts/tests/test_matches.py`

- [ ] **Step 1: Write the failing tests**

```python
"""matches: detector hits, env var reads, URL literals, migration dirs, MCP configs."""
from __future__ import annotations

from pathlib import Path

from matches import matches
from scanner import scan


def test_python_repo_matches(py_repo: Path) -> None:
    files, _ = scan(py_repo, max_files=1000)
    m = matches(files)
    storage = {s["detector"]: s for s in m["storage"]}
    assert set(storage) == {"sqlalchemy"}
    assert storage["sqlalchemy"]["evidence"] == [{"file": "src/demo/db/pg.py", "line": 1}]
    assert [e["detector"] for e in m["external"]] == ["requests"]
    assert m["env"] == {"API_KEY": [{"file": "src/demo/api/client.py", "line": 8}]}
    assert m["urls"] == [{"url": "https://api.example.com/v1", "evidence": [{"file": "src/demo/api/client.py", "line": 5}]}]
    assert m["migrations"] == ["alembic"]
    assert m["mcp"] == []


def test_ts_repo_matches(ts_repo: Path) -> None:
    files, _ = scan(ts_repo, max_files=1000)
    m = matches(files)
    assert [s["detector"] for s in m["storage"]] == ["supabase-js"]
    assert sorted(e["detector"] for e in m["external"]) == ["axios", "fetch-url"]
    assert sorted(m["env"]) == ["SUPABASE_KEY", "SUPABASE_URL"]


def test_mcp_servers_are_read_from_config(tmp_path: Path) -> None:
    (tmp_path / ".mcp.json").write_text('{"mcpServers": {"github": {"command": "x"}, "notion": {}}}', encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    assert matches(files)["mcp"] == [{"file": ".mcp.json", "servers": ["github", "notion"]}]
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_matches.py -q
```

Expected: `ModuleNotFoundError: No module named 'matches'`.

- [ ] **Step 3: Write matches.py**

```python
"""Apply the detector tables and the env/url patterns to every code file."""
from __future__ import annotations

import json
import re

from detectors import ENV_READ, MCP_CONFIG_FILES, MIGRATION_DIRS, URL_LITERAL, match_line
from scanner import SourceFile

EVIDENCE_CAP = 20


def matches(files: list[SourceFile]) -> dict:
    hits: dict[str, dict] = {}
    env: dict[str, list[dict]] = {}
    urls: dict[str, list[dict]] = {}
    env_re = {stack: re.compile(p) for stack, p in ENV_READ.items()}
    for f in files:
        if f.stack is None:
            continue
        for line_no, line in enumerate(f.lines, 1):
            ev = {"file": f.rel, "line": line_no}
            for d in match_line(line, f.stack):
                h = hits.setdefault(d.name, {
                    "detector": d.name, "lens": d.lens, "kind": d.kind, "stack": d.stack,
                    "count": 0, "evidence": [],
                })
                h["count"] += 1
                if len(h["evidence"]) < EVIDENCE_CAP:
                    h["evidence"].append(ev)
            for m in env_re[f.stack].finditer(line):
                name = next(g for g in m.groups() if g)
                env.setdefault(name, []).append(ev)
            for url in URL_LITERAL.findall(line):
                bucket = urls.setdefault(url, [])
                if len(bucket) < 3:
                    bucket.append(ev)
    dirs = {f.rel.rsplit("/", 1)[0] for f in files if "/" in f.rel}
    migrations = [d for d in MIGRATION_DIRS if any(x == d or x.startswith(d + "/") for x in dirs)]
    return {
        "storage": sorted((h for h in hits.values() if h["lens"] == "storage"), key=lambda h: h["detector"]),
        "external": sorted((h for h in hits.values() if h["lens"] == "external"), key=lambda h: h["detector"]),
        "env": dict(sorted(env.items())),
        "urls": [{"url": u, "evidence": e} for u, e in sorted(urls.items())],
        "migrations": migrations,
        "mcp": _mcp(files),
    }


def _mcp(files: list[SourceFile]) -> list[dict]:
    out: list[dict] = []
    for f in files:
        if f.rel.rsplit("/", 1)[-1] not in MCP_CONFIG_FILES:
            continue
        try:
            data = json.loads("\n".join(f.lines))
        except json.JSONDecodeError:
            continue
        servers = sorted(data.get("mcpServers", {}).keys()) if isinstance(data, dict) else []
        out.append({"file": f.rel, "servers": servers})
    return out
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_matches.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/matches.py scripts/tests/test_matches.py && git commit -qm "feat: storage, external, env, url and mcp matches"
```

---

### Task 10: entrypoints.py

**Files:**
- Create: `scripts/entrypoints.py`
- Test: `scripts/tests/test_entrypoints.py`

- [ ] **Step 1: Write the failing tests**

```python
"""entrypoints: ranked list of the ways a user or process enters the repo."""
from __future__ import annotations

from pathlib import Path

from entrypoints import entrypoints
from scanner import scan


def _kinds(items):
    return [(e["kind"], e["name"]) for e in items]


def test_python_entrypoints_ranked(py_repo: Path) -> None:
    files, _ = scan(py_repo, max_files=1000)
    e = entrypoints(files)
    assert _kinds(e)[:3] == [
        ("project.scripts", "demo"),
        ("readme_command", "python -m demo"),
        ("cli_framework", "src/demo/cli.py"),
    ]
    assert ("main_guard", "src/demo/cli.py") in _kinds(e)
    first = e[0]
    assert first["target"] == "demo.cli:main"
    assert first["evidence"] == [{"file": "pyproject.toml", "line": 6}]


def test_ts_entrypoints_ranked(ts_repo: Path) -> None:
    files, _ = scan(ts_repo, max_files=1000)
    e = entrypoints(files)
    kinds = _kinds(e)
    assert kinds[0] == ("bin", "tsdemo")
    assert ("http_route", "src/app/api/users/route.ts") in kinds
    assert ("npm_script", "dev") in kinds and ("npm_script", "build") in kinds
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_entrypoints.py -q
```

Expected: `ModuleNotFoundError: No module named 'entrypoints'`.

- [ ] **Step 3: Write entrypoints.py**

```python
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
    if any(f.rel.startswith("examples/") for f in files):
        out.append(_entry("examples_dir", "examples/", None, "examples/", 0))
    notebooks = [f for f in files if f.rel.endswith(".ipynb")]
    if notebooks:
        out.append(_entry("notebooks", f"{len(notebooks)} notebooks", None, notebooks[0].rel, 0))
    return sorted(out, key=lambda e: (-RANK[e["kind"]], e["name"]))


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
        m = re.match(r"""^\s*([\w.-]+)\s*=\s*['"]([^'"]+)['"]""", line)
        if m:
            out.append(_entry("project.scripts", m.group(1), m.group(2), f.rel, i))
    return out


def _package_json(f: SourceFile) -> list[dict]:
    try:
        data = json.loads("\n".join(f.lines))
    except json.JSONDecodeError:
        return []
    out: list[dict] = []
    bins = data.get("bin")
    if isinstance(bins, str):
        bins = {data.get("name", "bin"): bins}
    for name, target in (bins or {}).items():
        out.append(_entry("bin", name, target, f.rel, _line_of(f, f'"{name}"')))
    for name, cmd in (data.get("scripts") or {}).items():
        out.append(_entry("npm_script", name, cmd, f.rel, _line_of(f, f'"{name}"')))
    return out


def _line_of(f: SourceFile, needle: str) -> int:
    for i, line in enumerate(f.lines, 1):
        if needle in line:
            return i
    return 0


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
    for i, line in enumerate(f.lines, 1):
        if MAIN_GUARD_RE.match(line):
            out.append(_entry("main_guard", f.rel, None, f.rel, i))
        if CLI_IMPORT_RE.match(line) and not any(e["kind"] == "cli_framework" for e in out):
            out.append(_entry("cli_framework", f.rel, line.strip(), f.rel, i))
        if PY_ROUTE_RE.search(line):
            routes += 1
            first_route = first_route or i
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
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_entrypoints.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/entrypoints.py scripts/tests/test_entrypoints.py && git commit -qm "feat: ranked entrypoints"
```

---

### Task 11: infra.py

**Files:**
- Create: `scripts/infra.py`
- Test: `scripts/tests/test_infra.py`

- [ ] **Step 1: Write the failing tests**

```python
"""infra: docker, compose, devcontainer, CI, deploy configs, tests, tools."""
from __future__ import annotations

from pathlib import Path

from infra import infra
from scanner import scan


def test_python_repo_infra(py_repo: Path) -> None:
    files, _ = scan(py_repo, max_files=1000)
    i = infra(files)
    assert i["dockerfiles"] == [{"file": "Dockerfile", "base_image": "python:3.12-slim"}]
    assert i["compose"] == []
    assert i["devcontainer"] is False
    assert i["workflows"] == [{
        "file": ".github/workflows/ci.yml", "name": "CI",
        "triggers": ["push", "pull_request"], "matrix": ['python-version: ["3.12", "3.13"]'],
    }]
    assert i["deploy"] == []
    assert i["tests"] == {"dirs": {"tests": 1}, "loose_files": 0}
    assert i["tools"] == ["ruff"]


def test_ts_repo_infra(ts_repo: Path) -> None:
    files, _ = scan(ts_repo, max_files=1000)
    i = infra(files)
    assert i["deploy"] == ["vercel.json"]
    assert i["tools"] == ["typescript", "vitest"]
    assert i["tests"] == {"dirs": {}, "loose_files": 0}


def test_compose_services_and_inline_triggers(tmp_path: Path) -> None:
    (tmp_path / "compose.yaml").write_text("services:\n  web:\n    image: x\n  db:\n    image: y\nvolumes:\n  data:\n", encoding="utf-8")
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "deploy.yml").write_text("name: Deploy\non: [push, workflow_dispatch]\njobs: {}\n", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    i = infra(files)
    assert i["compose"] == [{"file": "compose.yaml", "services": ["web", "db"]}]
    assert i["workflows"][0]["triggers"] == ["push", "workflow_dispatch"]
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_infra.py -q
```

Expected: `ModuleNotFoundError: No module named 'infra'`.

- [ ] **Step 3: Write infra.py**

```python
"""Infrastructure evidence: containers, CI, deploy configs, test layout, tools."""
from __future__ import annotations

import json
import re

from scanner import SourceFile

COMPOSE_NAMES = ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")
DEPLOY_NAMES = ("vercel.json", "fly.toml", "serverless.yml", "serverless.yaml", "Procfile",
                "netlify.toml", "render.yaml", "app.yaml", "railway.json")
TEST_DIRS = ("tests", "test", "__tests__", "spec")
TEST_FILE_RE = re.compile(r"(^|/)(test_[^/]+\.py|[^/]+_test\.py|[^/]+\.(test|spec)\.(ts|tsx|js|jsx|mjs))$")
KNOWN_JS_TOOLS = ("typescript", "eslint", "prettier", "vitest", "jest", "playwright", "cypress", "biome", "tsx")
MATRIX_RE = re.compile(r"^\s*((python|node|os)-version:.*)$")


def infra(files: list[SourceFile]) -> dict:
    return {
        "dockerfiles": [_dockerfile(f) for f in files if f.rel.rsplit("/", 1)[-1].startswith("Dockerfile")],
        "compose": [_compose(f) for f in files if f.rel.rsplit("/", 1)[-1] in COMPOSE_NAMES],
        "devcontainer": any(f.rel.startswith(".devcontainer/") for f in files),
        "workflows": [_workflow(f) for f in files if f.rel.startswith(".github/workflows/") and f.rel.endswith((".yml", ".yaml"))],
        "deploy": sorted(f.rel for f in files if f.rel.rsplit("/", 1)[-1] in DEPLOY_NAMES) + _terraform(files),
        "tests": _tests(files),
        "tools": _tools(files),
    }


def _dockerfile(f: SourceFile) -> dict:
    base = next((line.split()[1] for line in f.lines if line.upper().startswith("FROM ") and len(line.split()) > 1), None)
    return {"file": f.rel, "base_image": base}


def _compose(f: SourceFile) -> dict:
    services: list[str] = []
    in_services = False
    for line in f.lines:
        if re.match(r"^services:\s*$", line):
            in_services = True
            continue
        if in_services and line and not line.startswith(" "):
            in_services = False
        m = re.match(r"^  ([\w.-]+):\s*$", line)
        if in_services and m:
            services.append(m.group(1))
    return {"file": f.rel, "services": services}


def _workflow(f: SourceFile) -> dict:
    name = next((line.split(":", 1)[1].strip().strip("'\"") for line in f.lines if re.match(r"^name:", line)), None)
    triggers: list[str] = []
    matrix = [m.group(1).strip() for m in map(MATRIX_RE.match, f.lines) if m]
    for i, line in enumerate(f.lines):
        m = re.match(r"^(on|'on'|\"on\"):\s*(.*)$", line)
        if not m:
            continue
        inline = m.group(2).strip()
        if inline:
            triggers = [t.strip() for t in inline.strip("[]").split(",") if t.strip()]
            break
        for nxt in f.lines[i + 1:]:
            if nxt and not nxt.startswith(" "):
                break
            key = re.match(r"^  ([\w_]+):", nxt)
            if key:
                triggers.append(key.group(1))
        break
    return {"file": f.rel, "name": name, "triggers": triggers, "matrix": matrix}


def _terraform(files: list[SourceFile]) -> list[str]:
    n = sum(1 for f in files if f.rel.endswith(".tf"))
    return [f"terraform ({n} .tf files)"] if n else []


def _tests(files: list[SourceFile]) -> dict:
    dirs: dict[str, int] = {}
    loose = 0
    for f in files:
        if not TEST_FILE_RE.search(f.rel):
            continue
        top = f.rel.split("/", 1)[0]
        if top in TEST_DIRS:
            dirs[top] = dirs.get(top, 0) + 1
        else:
            loose += 1
    return {"dirs": dict(sorted(dirs.items())), "loose_files": loose}


def _tools(files: list[SourceFile]) -> list[str]:
    tools: set[str] = set()
    for f in files:
        if f.rel == "pyproject.toml":
            for line in f.lines:
                m = re.match(r"^\s*\[tool\.([\w-]+)", line)
                if m and m.group(1) not in ("pdm", "poetry", "setuptools", "hatch"):
                    tools.add(m.group(1))
        elif f.rel == "package.json":
            try:
                data = json.loads("\n".join(f.lines))
            except json.JSONDecodeError:
                continue
            dev = data.get("devDependencies") or {}
            tools.update(t for t in KNOWN_JS_TOOLS if t in dev)
    return sorted(tools)
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_infra.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/infra.py scripts/tests/test_infra.py && git commit -qm "feat: infra evidence"
```

---

### Task 12: inventory.py (build + CLI)

**Files:**
- Create: `scripts/inventory.py`
- Test: `scripts/tests/test_inventory.py`

- [ ] **Step 1: Write the failing tests**

```python
"""inventory: orchestration and CLI."""
from __future__ import annotations

import json
from pathlib import Path

from inventory import build, main


def test_build_python_repo(py_repo: Path) -> None:
    inv = build(py_repo, max_files=1000)
    assert inv["meta"]["name"] == "demo"
    py = inv["code"]["python"]
    assert py["package_dir"] == "src/demo" and py["module"] == "demo"
    assert [u["name"] for u in py["units"]] == ["api", "cli", "core", "db"]
    assert py["layers"]["layers"] == [["api", "core"], ["db"], ["cli"]]
    assert py["contracts"][0]["name"] == "Repo"
    assert inv["code"]["ts"] is None
    assert inv["storage"][0]["detector"] == "sqlalchemy"
    assert inv["entrypoints"][0]["kind"] == "project.scripts"
    assert inv["infra"]["workflows"][0]["name"] == "CI"
    assert inv["unresolved"] == []


def test_build_ts_repo(ts_repo: Path) -> None:
    inv = build(ts_repo, max_files=1000)
    assert inv["code"]["python"] is None
    ts = inv["code"]["ts"]
    assert ts["source_root"] == "src"
    assert ts["layers"]["layers"] == [["lib"], ["services"], ["app"]]


def test_cli_writes_json_and_prints_ascii(py_repo: Path, tmp_path: Path, capsys) -> None:
    out = tmp_path / "inventory.json"
    assert main([str(py_repo), "--out", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["meta"]["name"] == "demo"
    printed = capsys.readouterr().out
    assert printed.isascii()
    assert "[ok] demo" in printed and "units=4" in printed
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_inventory.py -q
```

Expected: `ModuleNotFoundError: No module named 'inventory'`.

- [ ] **Step 3: Write inventory.py**

```python
"""Build inventory.json for a repository. Stdlib only. ASCII-only stdout.

Usage: python inventory.py <repo-root> --out <path/to/inventory.json> [--max-files N]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import py_analysis
import ts_analysis
from detectors import MAX_FILES_DEFAULT
from entrypoints import entrypoints
from graph import layers
from infra import infra
from matches import matches
from scanner import meta, scan

SCHEMA_VERSION = 1


def build(root: Path, max_files: int = MAX_FILES_DEFAULT) -> dict:
    started = time.time()
    files, capped = scan(root, max_files)
    unresolved: list[dict] = []

    python = None
    pkg = py_analysis.project_package(files)
    if pkg is not None:
        pkg_dir, module = pkg
        u = py_analysis.units(files, pkg_dir)
        g = py_analysis.import_graph(files, pkg_dir, module, set(u))
        unresolved.extend({"kind": "py_parse_failure", **x} for x in g["parse_failures"])
        unresolved.extend(
            {"kind": "py_other_top_package", "file": d, "line": 0}
            for d in py_analysis.other_top_packages(files, pkg_dir)
        )
        python = {
            "package_dir": pkg_dir, "module": module,
            "units": [u[k] for k in sorted(u)],
            "import_graph": g["edges"],
            "layers": layers(sorted(u), g["edges"]),
            "contracts": py_analysis.contracts(files, pkg_dir, g["edges"]),
        }

    ts = None
    if any(f.stack == "ts" for f in files):
        root_dir = ts_analysis.source_root(files)
        u = ts_analysis.units(files, root_dir)
        g = ts_analysis.import_graph(files, root_dir)
        unresolved.extend({"kind": "ts_alias_import", **x} for x in g["unresolved"])
        ts = {
            "source_root": root_dir,
            "units": [u[k] for k in sorted(u)],
            "import_graph": g["edges"],
            "layers": layers(sorted(u), g["edges"]),
            "contracts": ts_analysis.contracts(files, root_dir, g["edges"]),
        }

    m = matches(files)
    return {
        "schema": SCHEMA_VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "duration_s": round(time.time() - started, 2),
        "meta": meta(root, files, capped),
        "code": {"python": python, "ts": ts},
        "storage": m["storage"],
        "migrations": m["migrations"],
        "external": m["external"],
        "env": m["env"],
        "urls": m["urls"],
        "mcp": m["mcp"],
        "entrypoints": entrypoints(files),
        "infra": infra(files),
        "unresolved": unresolved,
    }


def summary(inv: dict) -> list[str]:
    m = inv["meta"]
    lines = [f"[ok] {m['name'] or '(unnamed)'} {m['version'] or ''} files={m['files']} code_lines={m['code_lines']} commit={m['commit'] or '-'}"]
    for stack in ("python", "ts"):
        c = inv["code"][stack]
        if c:
            lines.append(f"[ok] {stack}: units={len(c['units'])} edges={len(c['import_graph'])} layers={len(c['layers']['layers'])} cycles={len(c['layers']['cycles'])} contracts={len(c['contracts'])}")
    lines.append(f"[ok] storage={len(inv['storage'])} external={len(inv['external'])} env={len(inv['env'])} urls={len(inv['urls'])} mcp={len(inv['mcp'])}")
    lines.append(f"[ok] entrypoints={len(inv['entrypoints'])} workflows={len(inv['infra']['workflows'])} dockerfiles={len(inv['infra']['dockerfiles'])}")
    if m["capped"]:
        lines.append(f"[!] capped at {m['files']} files")
    if len(m["roots"]) > 1:
        lines.append(f"[!] {len(m['roots'])} roots found: {', '.join(m['roots'])} -> ask which one to map")
    if inv["unresolved"]:
        lines.append(f"[!] unresolved={len(inv['unresolved'])}")
    lines.append(f"[ok] done in {inv['duration_s']}s")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inventory a repository into JSON (stdlib only).")
    parser.add_argument("root")
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-files", type=int, default=MAX_FILES_DEFAULT)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"[x] not a directory: {root}")
        return 2
    inv = build(root, args.max_files)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(inv, indent=2, ensure_ascii=True), encoding="utf-8")
    for line in summary(inv):
        print(line)
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests -q
```

Expected: `34 passed` (all modules so far).

- [ ] **Step 5: Commit**

```bash
git add scripts/inventory.py scripts/tests/test_inventory.py && git commit -qm "feat: inventory build and CLI"
```

---

### Task 13: diff.py

**Files:**
- Create: `scripts/diff.py`
- Test: `scripts/tests/test_diff.py`

- [ ] **Step 1: Write the failing tests**

```python
"""diff: what changed between two inventories, rendered as ASCII."""
from __future__ import annotations

from diff import diff, render


def _inv(units, storage, external, entries):
    return {
        "code": {"python": {"units": [{"name": u} for u in units]}, "ts": None},
        "storage": [{"detector": s} for s in storage],
        "external": [{"detector": e} for e in external],
        "entrypoints": [{"kind": k, "name": n} for k, n in entries],
    }


def test_diff_lists_added_and_removed() -> None:
    old = _inv(["a", "b"], ["sqlalchemy"], [], [("project.scripts", "demo")])
    new = _inv(["a", "c"], [], ["requests"], [("project.scripts", "demo"), ("http_route", "api.py")])
    d = diff(old, new)
    assert d == {
        "units_added": ["c"], "units_removed": ["b"],
        "storage_added": [], "storage_removed": ["sqlalchemy"],
        "external_added": ["requests"], "external_removed": [],
        "entrypoints_added": ["http_route:api.py"], "entrypoints_removed": [],
    }
    text = render(d)
    assert "[+] unit c" in text and "[-] unit b" in text and "[-] storage sqlalchemy" in text


def test_no_changes() -> None:
    inv = _inv(["a"], [], [], [])
    assert render(diff(inv, inv)) == "[=] no changes since last inventory"
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_diff.py -q
```

Expected: `ModuleNotFoundError: No module named 'diff'`.

- [ ] **Step 3: Write diff.py**

```python
"""Compare two inventories and render the difference in ASCII."""
from __future__ import annotations


def _units(inv: dict) -> set[str]:
    names: set[str] = set()
    for stack in ("python", "ts"):
        c = (inv.get("code") or {}).get(stack)
        if c:
            names.update(u["name"] for u in c["units"])
    return names


def _names(items: list[dict], key: str) -> set[str]:
    return {i[key] for i in items}


def diff(old: dict, new: dict) -> dict:
    ou, nu = _units(old), _units(new)
    os_, ns = _names(old["storage"], "detector"), _names(new["storage"], "detector")
    oe, ne = _names(old["external"], "detector"), _names(new["external"], "detector")
    op = {f"{e['kind']}:{e['name']}" for e in old["entrypoints"]}
    np_ = {f"{e['kind']}:{e['name']}" for e in new["entrypoints"]}
    return {
        "units_added": sorted(nu - ou), "units_removed": sorted(ou - nu),
        "storage_added": sorted(ns - os_), "storage_removed": sorted(os_ - ns),
        "external_added": sorted(ne - oe), "external_removed": sorted(oe - ne),
        "entrypoints_added": sorted(np_ - op), "entrypoints_removed": sorted(op - np_),
    }


def render(d: dict) -> str:
    lines: list[str] = []
    for key, label in (("units", "unit"), ("storage", "storage"), ("external", "external"), ("entrypoints", "entrypoint")):
        lines.extend(f"[+] {label} {x}" for x in d[f"{key}_added"])
        lines.extend(f"[-] {label} {x}" for x in d[f"{key}_removed"])
    return "\n".join(lines) if lines else "[=] no changes since last inventory"
```

- [ ] **Step 4: Wire `--diff` into inventory.py**

In `scripts/inventory.py`, add the import and the option. Replace the `main` function body between `inv = build(...)` and the summary loop:

```python
    inv = build(root, args.max_files)
    if args.diff:
        previous = Path(args.diff)
        if previous.is_file():
            from diff import diff, render
            old = json.loads(previous.read_text(encoding="utf-8"))
            print("[diff] against " + str(previous))
            print(render(diff(old, inv)))
        else:
            print(f"[diff] no previous inventory at {previous}")
    out = Path(args.out)
```

and add the argument after `--max-files`:

```python
    parser.add_argument("--diff", help="path to a previous inventory.json to compare against")
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests -q
```

Expected: `36 passed`.

- [ ] **Step 6: Commit**

```bash
git add scripts/diff.py scripts/tests/test_diff.py scripts/inventory.py && git commit -qm "feat: inventory diff and --diff flag"
```

---

### Task 14: templates/architecture.html

The fixed design. The model replaces the content between each `<!-- LENS:x -->` / `<!-- /LENS:x -->` pair and the `{{...}}` tokens in the hero and footer. No other edits.

**Files:**
- Create: `templates/architecture.html`

- [ ] **Step 1: Write the template**

```html
<title>{{PROJECT_NAME}}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --bg:#F2F4F6; --surface:#FFFFFF; --ink:#16202B; --muted:#5C6B7A; --line:#D5DBE2; --line-soft:#E6EAEF;
  --accent:#0E6B84; --accent-soft:#DDEEF3; --accent-ink:#0A4F62;
  --yes:#2F7D4E; --yes-soft:#DFF0E5; --warn:#9A6A10; --warn-soft:#F8EDD3; --no:#B4423B; --no-soft:#F6E0DE;
  --code:#D9EEF4; --storage:#E2EFE6; --external:#E8E5F6; --flow:#F3ECDC; --infra:#ECEFF3;
  --code-bg:#EEF1F4;
  --serif:"IBM Plex Serif",Georgia,"Times New Roman",serif;
  --sans:"IBM Plex Sans","Segoe UI",Helvetica,Arial,sans-serif;
  --mono:"IBM Plex Mono",Consolas,"Courier New",monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#0F1418; --surface:#161C23; --ink:#E4E9EE; --muted:#93A0AD; --line:#2A343F; --line-soft:#212A34;
    --accent:#55B6D0; --accent-soft:#14323C; --accent-ink:#8ED2E4;
    --yes:#6CC48E; --yes-soft:#17301F; --warn:#E0B65A; --warn-soft:#3A2E12; --no:#E38680; --no-soft:#3A1E1C;
    --code:#14323C; --storage:#17301F; --external:#26223C; --flow:#332C1A; --infra:#1C232B;
    --code-bg:#1D252E;
  }
}
:root[data-theme="dark"]{
  --bg:#0F1418; --surface:#161C23; --ink:#E4E9EE; --muted:#93A0AD; --line:#2A343F; --line-soft:#212A34;
  --accent:#55B6D0; --accent-soft:#14323C; --accent-ink:#8ED2E4;
  --yes:#6CC48E; --yes-soft:#17301F; --warn:#E0B65A; --warn-soft:#3A2E12; --no:#E38680; --no-soft:#3A1E1C;
  --code:#14323C; --storage:#17301F; --external:#26223C; --flow:#332C1A; --infra:#1C232B;
  --code-bg:#1D252E;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.55}
a{color:var(--accent-ink)}
.page{display:grid;grid-template-columns:1fr;max-width:1180px;margin:0 auto;padding:0 20px 80px}
@media(min-width:1000px){.page{grid-template-columns:220px minmax(0,1fr);gap:48px}}
nav.toc{display:none}
@media(min-width:1000px){
  nav.toc{display:block;position:sticky;top:24px;align-self:start;padding-top:56px;font-size:13.5px}
  nav.toc ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px}
  nav.toc a{display:block;padding:5px 10px;border-left:2px solid var(--line);color:var(--muted);text-decoration:none}
  nav.toc a:hover,nav.toc a:focus-visible{color:var(--ink);border-left-color:var(--accent);outline:none}
  nav.toc .lbl{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);padding:0 10px 8px}
}
main{min-width:0}
header.hero{padding:56px 0 28px;border-bottom:1px solid var(--line)}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent-ink)}
h1{font-family:var(--serif);font-weight:500;font-size:clamp(30px,4vw,42px);line-height:1.12;margin:10px 0 14px;text-wrap:balance;max-width:22ch}
.lede{font-size:18px;max-width:62ch;margin:0 0 20px}
.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;max-width:640px}
@media(max-width:640px){.stats{grid-template-columns:1fr}}
.stat{padding:12px 16px;border:1px solid var(--line);background:var(--surface);border-radius:6px}
.stat b{display:block;font-family:var(--serif);font-size:26px;font-weight:500;font-variant-numeric:tabular-nums}
.stat span{font-size:13px;color:var(--muted)}
section{padding:40px 0 8px;border-bottom:1px solid var(--line-soft)}
section:last-of-type{border-bottom:0}
h2{font-family:var(--serif);font-weight:500;font-size:28px;line-height:1.2;margin:0 0 6px;text-wrap:balance}
h3{font-family:var(--serif);font-weight:600;font-size:19px;margin:28px 0 8px}
p{max-width:68ch;margin:0 0 14px}
.sub{color:var(--muted);max-width:68ch;margin:0 0 20px;font-size:15.5px}
ul{max-width:68ch;padding-left:20px;margin:0 0 14px}
li{margin:4px 0}
code{font-family:var(--mono);font-size:.88em;background:var(--code-bg);padding:1px 5px;border-radius:3px}
pre{font-family:var(--mono);font-size:13px;line-height:1.5;background:var(--code-bg);padding:14px 16px;border-radius:6px;overflow-x:auto;margin:0 0 16px;max-width:760px}
pre code{background:none;padding:0;font-size:inherit}
.tablewrap{overflow-x:auto;margin:0 0 20px;border:1px solid var(--line);border-radius:6px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:14.5px}
th{text-align:left;font-family:var(--mono);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);padding:10px 12px;border-bottom:1px solid var(--line)}
td{padding:9px 12px;border-bottom:1px solid var(--line-soft);vertical-align:top}
tr:last-child td{border-bottom:0}
td.name{font-family:var(--mono);font-size:13px;white-space:nowrap}
td.num{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
td.src{font-family:var(--mono);font-size:12px;color:var(--muted);white-space:nowrap}
.group td.grp{font-family:var(--serif);font-weight:600;font-size:15px;background:var(--bg);padding:8px 12px}
.pill{display:inline-block;font-family:var(--mono);font-size:11.5px;padding:2px 8px;border-radius:999px;border:1px solid transparent;white-space:nowrap}
.pill.yes{color:var(--yes);background:var(--yes-soft)}
.pill.warn{color:var(--warn);background:var(--warn-soft)}
.pill.no{color:var(--no);background:var(--no-soft)}
.pill.mute{color:var(--muted);border-color:var(--line)}
.note{border-left:3px solid var(--accent);background:var(--surface);padding:12px 16px;margin:0 0 18px;max-width:760px;border-radius:0 6px 6px 0}
.note.warn{border-left-color:var(--warn)}
.note.empty{border-left-color:var(--muted);color:var(--muted)}
.note p:last-child{margin-bottom:0}
.note .t{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:4px}
figure{margin:20px 0 24px;max-width:860px}
figure svg{max-width:100%;height:auto;display:block;color:var(--ink);font-family:var(--sans)}
figcaption{font-size:13.5px;color:var(--muted);margin-top:8px;max-width:68ch}
.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;max-width:820px;margin:0 0 20px}
@media(max-width:700px){.grid2{grid-template-columns:1fr}}
.card{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:14px 16px}
.card h4{font-family:var(--serif);font-weight:600;font-size:16px;margin:0 0 6px}
.card p{font-size:14.5px;margin:0 0 6px;max-width:none}
.card .who{font-family:var(--mono);font-size:12px;color:var(--muted)}
.card.code{border-top:3px solid #3A9DB8}.card.storage{border-top:3px solid #4EA26E}.card.external{border-top:3px solid #8C7FD6}.card.flow{border-top:3px solid #C49A3C}.card.infra{border-top:3px solid var(--muted)}
.kv{display:grid;grid-template-columns:auto 1fr;gap:6px 18px;font-size:14.5px;max-width:760px;margin:0 0 16px}
.kv dt{font-family:var(--mono);font-size:13px;color:var(--muted);white-space:nowrap}
.kv dd{margin:0}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);font-size:13px;color:var(--muted);max-width:68ch}
</style>

<div class="page">
<nav class="toc" aria-label="Contenido">
  <div class="lbl">{{NAV_LABEL}}</div>
  <ol>
    <li><a href="#context">{{NAV_CONTEXT}}</a></li>
    <li><a href="#code">{{NAV_CODE}}</a></li>
    <li><a href="#contracts">{{NAV_CONTRACTS}}</a></li>
    <li><a href="#storage">{{NAV_STORAGE}}</a></li>
    <li><a href="#external">{{NAV_EXTERNAL}}</a></li>
    <li><a href="#flow">{{NAV_FLOW}}</a></li>
    <li><a href="#infra">{{NAV_INFRA}}</a></li>
  </ol>
</nav>

<main>
<header class="hero">
  <div class="eyebrow">{{PROJECT_NAME}} · {{VERSION}} · {{COMMIT}}</div>
  <h1>{{TITLE}}</h1>
  <p class="lede">{{LEDE}}</p>
  <div class="stats">
    <div class="stat"><b>{{STAT_UNITS}}</b><span>{{STAT_UNITS_LABEL}}</span></div>
    <div class="stat"><b>{{STAT_LINES}}</b><span>{{STAT_LINES_LABEL}}</span></div>
    <div class="stat"><b>{{STAT_EXTERNAL}}</b><span>{{STAT_EXTERNAL_LABEL}}</span></div>
  </div>
</header>

<section id="context">
<!-- LENS:context -->
<!-- system context diagram: repo center, storage left, external right, users/entrypoints top, infra bottom -->
<!-- /LENS:context -->
</section>

<section id="code">
<!-- LENS:code -->
<!-- layers diagram, units table (name, files, lines, role, imports from), error taxonomy, tests -->
<!-- /LENS:code -->
</section>

<section id="contracts">
<!-- LENS:contracts -->
<!-- one card per contract: implement X, inherit Y, implementers -->
<!-- /LENS:contracts -->
</section>

<section id="storage">
<!-- LENS:storage -->
<!-- table: detector, kind, count, first evidence path:line; migrations dirs -->
<!-- /LENS:storage -->
</section>

<section id="external">
<!-- LENS:external -->
<!-- tables: http clients and sdks; url literals; env vars; mcp servers -->
<!-- /LENS:external -->
</section>

<section id="flow">
<!-- LENS:flow -->
<!-- main entrypoint drawn as a flow; other entrypoints in a table -->
<!-- /LENS:flow -->
</section>

<section id="infra">
<!-- LENS:infra -->
<!-- containers, ci workflows (triggers, matrix), deploy configs, tests layout, tools -->
<!-- /LENS:infra -->
</section>

<footer>{{FOOTER}}</footer>
</main>
</div>
```

- [ ] **Step 2: Sanity check the markers**

```bash
grep -c 'LENS:' ../templates/architecture.html
```

Expected: `14` (seven open, seven close).

- [ ] **Step 3: Commit**

```bash
git add templates/architecture.html && git commit -qm "feat: fixed page template with lens markers"
```

---

### Task 15: SKILL.md

**Files:**
- Create: `SKILL.md`

- [ ] **Step 1: Write SKILL.md**

````markdown
---
name: map-project-architecture
description: Map a Python or TypeScript repository into one evidence-backed HTML architecture page — import layers, contracts, storage, external connections, user flow and infra — written to docs/architecture/index.html and published as an Artifact. Every claim carries a file and line from scripts/inventory.py; a lens with no evidence says so instead of guessing. Use when the user says "map the architecture", "arquitectura del proyecto", "map-project-architecture", or wants an onboarding page for a codebase.
disable-model-invocation: true
---

# map-project-architecture

One invocation, one page. The page is built from `inventory.json`, never from
memory or the README. The README is read for names and for the user flow only.

## 0. Ground rules

- **Evidence or nothing.** Every row, card and diagram box comes from an item in
  `inventory.json` and shows its `file:line`. A lens with no items renders the
  empty-state block naming what was searched.
- **Never fill from general knowledge.** If the JSON does not say the project uses
  Postgres, the page does not say it either.
- **Fixed design.** Use `templates/architecture.html` as is. Replace only the
  `{{TOKENS}}` and the content between `<!-- LENS:x -->` markers.
- **Language** of the page: the language of the invoking message.
- **Write only** under `docs/architecture/` in the target repo.

## 1. Inventory

```bash
python "<skill-dir>/scripts/inventory.py" <repo-root> --out "<scratchpad>/inventory.json" --diff "<repo-root>/docs/architecture/inventory.json"
```

`<skill-dir>` is this file's directory. Read the printed summary:

- `[!] N roots found` -> ask once which root to map, then rerun with that root.
- `[!] capped` -> say so in the footer.
- `[diff] ...` -> keep those lines; they go in the footer as "what changed".
- Script cannot run (no Python, crash) -> follow section 6 and mark the page
  "confianza reducida / reduced confidence" in the eyebrow.

Then Read `inventory.json` in full.

## 2. Names and flow (README pass)

Read `README.md` and the top level of `docs/` only to learn: what the project
calls its stages, who the user is, and the first runnable example. Do not take
architecture claims from them.

## 3. Main entrypoint

Take `entrypoints[0]` (already ranked: project.scripts / bin, README command,
routes, `__main__`, CLI framework, npm scripts, main guards). If the top two
share the same rank and differ in kind, ask once which one the page should draw.

## 4. Fill the seven blocks

Each block goes between its markers. Every table has a `fuente` column with
`file:line` from `evidence[0]`. Empty state is:

```html
<div class="note empty"><div class="t">No encontrado</div><p>Buscamos: <detector names or patterns>. Nada coincidio en <N> archivos de codigo.</p></div>
```

| Block | Source in JSON | What to draw or list |
|---|---|---|
| context | meta, storage, external, entrypoints, infra | SVG: repo box center with name and unit count; storage boxes left (one per detector kind); external boxes right (http clients, SDKs, MCP servers); entrypoints top; infra bottom (containers, CI, deploy). Every box shows its count. Arrows labeled "lee/escribe", "llama", "entra por", "corre en". Empty side -> a dashed box "nada detectado". |
| code | code.python / code.ts: units, import_graph, layers | SVG layers: one band per `layers.layers[i]`, bottom = layer 0; units in the same band drawn side by side; arrows down labeled "importa de" from the edges; units that share a band and are not in a `cycles` entry have no import between them, name the ones that matter in the caption ("X, Y y Z no se importan entre si"); `cycles` drawn with a red pill and named. Then the units table: name, kind, files, lines, imports from (from edges), fuente (package_dir). If both stacks exist, two diagrams. |
| contracts | code.*.contracts | One card per contract: name, kind, "implementas: <abstract_methods>", implementers with unit, fuente. |
| storage | storage, migrations | Table: detector, kind, stack, count, fuente. Migrations dirs as pills. |
| external | external, urls, env, mcp | Table of clients and SDKs; table of URL literals (host only in the name column, full URL in a code cell); env var names with first fuente (never values); MCP servers per config file. |
| flow | entrypoints, code layers, README example | SVG left-to-right: entrypoint -> the units it reaches (follow edges from the entrypoint's unit down the layers) -> outputs (storage kinds, file writes). Below, table of the other entrypoints: kind, name, target, fuente. |
| infra | infra | Cards: containers (base image), compose services, devcontainer, CI workflows (name, triggers, matrix), deploy configs, tests by dir, tools. |

Hero tokens: `PROJECT_NAME`, `VERSION`, `COMMIT` from meta; `TITLE` a one-line
statement of what the repo is, in the page language; `LEDE` two sentences from
the README pass; `STAT_UNITS` = total units across stacks, `STAT_LINES` =
`meta.code_lines`, `STAT_EXTERNAL` = `len(external) + len(mcp servers)`.
`NAV_*` labels in the page language.

`FOOTER`: "Generado desde inventory.json · commit <sha> · <date> · <files> archivos, <code_lines> lineas · lentes vacias: <list or 'ninguna'> · <diff lines or 'primera corrida'>" plus "capped" if set.

## 5. Diagrams

Inline SVG, `viewBox` sized to content, `currentColor` strokes, one
`<marker>` arrowhead, boxes filled with the lens token (`var(--code)`,
`var(--storage)`, `var(--external)`, `var(--flow)`, `var(--infra)`), 12-13px
labels, `<figure>` + `<figcaption>` stating the claim, `role="img"` +
`aria-label`. Grid: 20px gutters, boxes on shared baselines.

## 6. Fallback when the script cannot run

Run these by hand and build a reduced `inventory.json` with the same shape:

- units: `find src -name __init__.py` (Python) or `ls src` (TS);
- imports: `rg -n "^(from|import) <package>" <package_dir>` per unit;
- contracts: `rg -n "abstractmethod|\(ABC\)|Protocol\)|export interface|abstract class"`;
- storage / external: the recipes table below;
- entrypoints: `rg -n "project.scripts|\"bin\"|__main__|if __name__"`;
- infra: `ls Dockerfile* compose* .devcontainer .github/workflows`.

Recipes (generated by `python scripts/detectors.py` is not a CLI; paste from
`grep_recipes()` when the table changes):

<!-- run: python -c "import sys; sys.path.insert(0,'scripts'); from detectors import grep_recipes; print(grep_recipes())" and paste below -->

## 7. Publish

1. Load the `artifact-design` skill (required before writing any artifact).
2. Write `<repo-root>/docs/architecture/index.html` and copy `inventory.json`
   next to it.
3. Publish `index.html` with the Artifact tool. Favicon on first publish: a
   single emoji chosen for the project. Title = `PROJECT_NAME`.
4. Report: the Artifact URL, the file path, the empty lenses, and the diff lines.
````

- [ ] **Step 2: Paste the recipes table into section 6**

```bash
python -c "import sys; sys.path.insert(0,'scripts'); from detectors import grep_recipes; print(grep_recipes())" > "$TMP/recipes.md" && wc -l "$TMP/recipes.md"
```

Expected: `38` lines (header, separator, 36 detectors). Insert the table content below the `<!-- run: ... -->` comment in `SKILL.md` (open the file, paste after that line).

- [ ] **Step 3: Verify the frontmatter parses**

```bash
head -5 SKILL.md
```

Expected: the four frontmatter lines between `---` fences, `name: map-project-architecture` first.

- [ ] **Step 4: Commit**

```bash
git add SKILL.md && git commit -qm "feat: SKILL.md procedure, evidence rules and fallback recipes"
```

---

### Task 16: Acceptance on the reference repo

**Files:** none created in the skill. Output goes to the scratchpad only (do not write into `S_Portfolio-Construction` during acceptance).

- [ ] **Step 1: Run the inventory on the reference repo**

```bash
python inventory.py /c/Proyectos/S_Portfolio-Construction --out "$TMP/pc-inventory.json"
```

Expected summary contains:
- `[ok] kaxanuk.portfolio_construction 1.28.0`
- `[ok] python: units=16 edges=` (any number) `layers=` (4 or 5) `cycles=0 contracts=` (6 or 7)
- `[ok] storage=` at least 1 (the `parquet-csv-write` detector should fire on the output handlers) and `external=0` (no HTTP clients or SDKs in this repo)
- `[ok] done in` under `30.0s`

- [ ] **Step 2: Check the three reference findings**

```bash
python - <<'PY'
import json, os
inv = json.load(open(os.path.expandvars("$TMP/pc-inventory.json"), encoding="utf-8"))
py = inv["code"]["python"]
units = {u["name"] for u in py["units"]}
assert units == {"builders","config_handlers","entities","enums","exceptions","helpers","input_handlers","market_data_pipeline_services","modules","output_handlers","pipeline","selection","services","sizing","timing","visualization"}, units
stage_layers = {u: i for i, layer in enumerate(py["layers"]["layers"]) for u in layer}
assert stage_layers["selection"] == stage_layers["sizing"] == stage_layers["timing"], stage_layers
assert py["layers"]["cycles"] == [], py["layers"]["cycles"]
edges = {(e["from"], e["to"]) for e in py["import_graph"]}
assert not any((a, b) in edges for a in ("selection","sizing","timing") for b in ("selection","sizing","timing") if a != b)
names = {c["name"] for c in py["contracts"]}
assert {"SelectionInterface","SizingInterface","TimingInterface","OutputHandlerInterface","InputHandlerInterface","ConfiguratorInterface"} <= names, names  # BaseOutputHandler may also appear
sizing = next(c for c in py["contracts"] if c["name"] == "SizingInterface")
assert len(sizing["implementers"]) == 14, len(sizing["implementers"])
print("[ok] reference findings reproduced")
PY
```

Expected: `[ok] reference findings reproduced`. If `units` fails because `services` or `modules` is missing, check `py_analysis.unit_of` against the actual tree before changing the assertion.

- [ ] **Step 3: Full test run**

```bash
python -m pytest tests -q
```

Expected: `36 passed`.

- [ ] **Step 4: Commit the acceptance note**

Append to `docs/2026-09-03-map-project-architecture-design.md` under `## Acceptance`:

```markdown
2026-09-03: inventory reproduced the reference page's code lens on
S_Portfolio-Construction (16 units, three independent stage pairs, six
contracts, 14 SizingInterface implementers). Next + Supabase and mixed repos
pending.
```

```bash
git add docs && git commit -qm "docs: acceptance on the reference repo"
```

---

### Task 17: Mirror to the SKILLS folder

**Files:**
- Create: `C:\Users\alanv\OneDrive\Documentos\GitHub\SKILLS\map-project-architecture\` (copy)

- [ ] **Step 1: Copy the skill without git internals and caches**

```bash
SRC="$HOME/.claude/skills/map-project-architecture"; DST="/c/Users/alanv/OneDrive/Documentos/GitHub/SKILLS/map-project-architecture"; mkdir -p "$DST" && rsync -a --exclude .git --exclude __pycache__ --exclude .pytest_cache "$SRC/" "$DST/" 2>/dev/null || (cd "$SRC" && tar --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache -cf - . | (cd "$DST" && tar -xf -)) && find "$DST" -type f | wc -l
```

Expected: a file count equal to `git ls-files | wc -l` run in `$SRC`.

---

## Self-review

**Spec coverage.** Six lenses: code (Tasks 5-7, template, SKILL 4), contracts (6, 8), storage and external (9), user flow (10, SKILL 3-4), infra (11). Evidence on every item: every builder emits `evidence` or `file`/`line`. Empty-state rule: SKILL 4. Monorepo ask: `meta.roots` + SKILL 1. Cap 20k: `MAX_FILES_DEFAULT` + summary `[!] capped`. TS alias paths unresolved: Task 8. Re-run diff: Task 13. Reference acceptance: Task 16. Mirror: Task 17. Deviation from spec: `.gitignore` not honored (stated in the header).

**Placeholders.** None: every step has its code or exact command. The recipes table in SKILL.md is generated by a command in Task 15 step 2, not hand-written.

**Type consistency.** `SourceFile(path, rel, stack, lines)` used identically in scanner, py_analysis, ts_analysis, matches, entrypoints, infra. `layers(units: list[str], edges: list[dict]) -> {"layers","cycles"}` consumed by inventory and SKILL (`independent_pairs` dropped after review: same-band membership already implies no edge outside a cycle). `import_graph` takes the unit set; `contracts` takes the edges. Edge dicts always `{"from","to","count"}`. Contract dicts from both stacks share `name, kind, unit, abstract_methods, implementers, evidence`. `build()` keys match `summary()`, `diff()` and SKILL section 4.

**Test count check.** detectors 7 + scanner 4 + py_analysis 4 + graph 3 + ts_analysis 5 + matches 3 + entrypoints 2 + infra 3 + inventory 3 = 34 by Task 12; + diff 2 = 36.
