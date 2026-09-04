"""Apply the detector tables and the env/url patterns to every code file."""
from __future__ import annotations

import json
import re

from detectors import ENV_READ, MCP_CONFIG_FILES, MIGRATION_DIRS, URL_LITERAL, match_line
from scanner import NON_ROOT_SEGMENTS, SourceFile

EVIDENCE_CAP = 20
URL_EVIDENCE_CAP = 3


def matches(files: list[SourceFile]) -> dict:
    hits: dict[str, dict] = {}
    env: dict[str, dict] = {}
    urls: dict[str, dict] = {}
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
            pattern = env_re.get(f.stack)
            for m in pattern.finditer(line) if pattern else ():
                name = next(g for g in m.groups() if g)
                # Capped evidence without a count reads as "used once".
                bucket = env.setdefault(name, {"count": 0, "evidence": []})
                bucket["count"] += 1
                if len(bucket["evidence"]) < EVIDENCE_CAP:
                    bucket["evidence"].append(ev)
            for url in URL_LITERAL.findall(line):
                bucket = urls.setdefault(url, {"count": 0, "evidence": []})
                bucket["count"] += 1
                if len(bucket["evidence"]) < URL_EVIDENCE_CAP:
                    bucket["evidence"].append(ev)
    migrations = _migration_dirs(files)
    return {
        "storage": sorted((h for h in hits.values() if h["lens"] == "storage"), key=lambda h: h["detector"]),
        "external": sorted((h for h in hits.values() if h["lens"] == "external"), key=lambda h: h["detector"]),
        "env": dict(sorted(env.items())),
        "urls": [{"url": u, **v} for u, v in sorted(urls.items())],
        "migrations": migrations,
        "mcp": _mcp(files),
    }


def _migration_dirs(files: list[SourceFile]) -> list[str]:
    """Migration directories wherever they sit. `myapp/migrations/` is as real
    as a root one, and reporting it as `migrations` loses where it actually is."""
    dirs: set[str] = set()
    for f in files:
        parts = f.rel.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:i]))
    return sorted(
        d for d in dirs
        if not NON_ROOT_SEGMENTS.intersection(d.split("/"))
        and (d.rsplit("/", 1)[-1] in MIGRATION_DIRS
             or "/".join(d.split("/")[-2:]) in MIGRATION_DIRS)
    )


def _mcp(files: list[SourceFile]) -> list[dict]:
    out: list[dict] = []
    for f in files:
        if f.rel.rsplit("/", 1)[-1] not in MCP_CONFIG_FILES:
            continue
        # A config under tests/ or fixtures/ is a sample, not this repo's wiring.
        if NON_ROOT_SEGMENTS.intersection(f.rel.split("/")[:-1]):
            continue
        try:
            data = json.loads("\n".join(f.lines))
        except json.JSONDecodeError:
            continue
        servers = sorted(data.get("mcpServers", {}).keys()) if isinstance(data, dict) else []
        out.append({"file": f.rel, "servers": servers})
    return out
