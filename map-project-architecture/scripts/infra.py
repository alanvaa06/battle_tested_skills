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
# A matrix declares a list; `python-version: ${{ matrix.python-version }}` consumes one.
MATRIX_RE = re.compile(r"^\s*((?:python|node|os)-version:\s*\[[^\]]*\])")


def infra(files: list[SourceFile]) -> dict:
    return {
        "dockerfiles": _sorted(_dockerfile(f) for f in files if f.rel.rsplit("/", 1)[-1].startswith("Dockerfile")),
        "compose": _sorted(_compose(f) for f in files if f.rel.rsplit("/", 1)[-1] in COMPOSE_NAMES),
        "devcontainer": any(f.rel.startswith(".devcontainer/") for f in files),
        "workflows": _sorted(_workflow(f) for f in files if f.rel.startswith(".github/workflows/") and f.rel.endswith((".yml", ".yaml"))),
        "deploy": sorted(f.rel for f in files if f.rel.rsplit("/", 1)[-1] in DEPLOY_NAMES) + _terraform(files),
        "tests": _tests(files),
        "tools": _tools(files),
    }


def _sorted(items) -> list[dict]:
    """The scan order of a directory is not the reader's order."""
    return sorted(items, key=lambda d: d["file"])


def _dockerfile(f: SourceFile) -> dict:
    """The LAST `FROM`: in a multi-stage build the earlier ones are throwaway
    builders, and the final stage is what actually ships. That stage can itself
    be `FROM <earlier-stage-alias>`, so resolve aliases back to a real image."""
    alias: dict[str, str] = {}
    base = None
    for line in f.lines:
        parts = line.split()
        if len(parts) > 1 and parts[0].upper() == "FROM":
            base = parts[1]
            if len(parts) > 3 and parts[2].upper() == "AS":
                alias[parts[3]] = base
    seen: set[str] = set()
    while base in alias and base not in seen:
        seen.add(base)
        base = alias[base]
    return {"file": f.rel, "base_image": base}


def _compose(f: SourceFile) -> dict:
    """Service names under `services:`, at whatever indent this file happens to use."""
    services: list[str] = []
    in_services = False
    indent: str | None = None
    for line in f.lines:
        if re.match(r"^services:\s*(#.*)?$", line):
            in_services, indent = True, None
            continue
        if not in_services or not line.strip():
            continue
        # A comment can sit at any column: learning the indent from one would
        # lose every service under it.
        if line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            in_services = False
            continue
        if indent is None:
            indent = line[: len(line) - len(line.lstrip(" "))]
        m = re.match(rf"^{re.escape(indent)}([\w.-]+):\s*(#.*)?$", line)
        if m:
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
        # Two spaces is a convention, not a rule: learn the indent from the file.
        indent: str | None = None
        for nxt in f.lines[i + 1:]:
            if nxt and not nxt.startswith(" "):
                break
            if not nxt.strip() or nxt.lstrip().startswith("#"):
                continue
            if indent is None:
                indent = nxt[: len(nxt) - len(nxt.lstrip(" "))]
            key = re.match(rf"^{re.escape(indent)}([\w_]+):", nxt)
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
        # A monorepo keeps its tests at packages/<name>/tests/, not at the root.
        bucket = next((p for p in f.rel.split("/")[:-1] if p in TEST_DIRS), None)
        if bucket:
            dirs[bucket] = dirs.get(bucket, 0) + 1
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
