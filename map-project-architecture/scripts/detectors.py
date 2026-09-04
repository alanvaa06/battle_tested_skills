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

# consumed by matches.py (Task 9)
MIGRATION_DIRS: tuple[str, ...] = ("alembic", "migrations", "prisma/migrations", "supabase/migrations")
# consumed by matches.py (Task 9)
MCP_CONFIG_FILES: tuple[str, ...] = (".mcp.json", "claude_desktop_config.json")


def _py_import(module: str) -> str:
    return rf"^\s*(from\s+{module}(\.|\s)|import\s+{module}(\.|\s|$))"


def _ts_import(spec: str) -> str:
    """Import/require of `spec`, ignoring comment lines and partial package names.

    The line must not open with `//`, `*` or `/*`, and the spec must end at a
    package boundary -- a closing quote or a `/` subpath -- so `axios` matches
    `'axios'` and `'axios/lib/x'` but never `'axios-retry'`. A scope prefix
    written with a trailing `/` (`@supabase/`) already names that boundary, so
    the slash is dropped and the lookahead supplies it.
    """
    stem = spec[:-1] if spec.endswith("/") else spec
    return rf"""^(?!\s*(//|\*|/\*)).*(from\s+['"]{stem}|require\(\s*['"]{stem})(?=['"/])"""


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
    Detector("pg", "storage", "sql", "ts", _ts_import("pg"), "rg -n \"from ['\\\"]pg['\\\"]\""),
    Detector("supabase-js", "storage", "baas", "ts", _ts_import("@supabase/"), "rg -n '@supabase/'"),
    Detector("mongoose", "storage", "nosql", "ts", _ts_import("mongoose"), "rg -n 'mongoose'"),
    Detector("ioredis", "storage", "cache", "ts", _ts_import("(ioredis|redis)"), "rg -n \"ioredis|from ['\\\"]redis['\\\"]\""),
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
    Detector("ky", "external", "http_client", "ts", _ts_import("ky"), "rg -n \"from ['\\\"]ky['\\\"]\""),
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

# `$`, `{` and `}` end the literal so a template stops at its interpolation.
URL_LITERAL: re.Pattern[str] = re.compile(r"""['"`](https?://[^'"`\s)${}]+)""")

# Compiled once at import: match_line runs this table against every line of every file.
_COMPILED: tuple[tuple[Detector, re.Pattern[str]], ...] = tuple(
    (d, re.compile(d.pattern)) for d in ALL_DETECTORS
)


def match_line(line: str, stack: str) -> list[Detector]:
    """Every detector of this stack (or 'any') whose pattern hits the line."""
    return [d for d, rx in _COMPILED if d.stack in (stack, "any") and rx.search(line)]


def grep_recipes() -> str:
    """Markdown table of manual recipes: the fallback when the script cannot run."""
    rows = ["| lens | detector | kind | stack | grep |", "|---|---|---|---|---|"]
    for d in ALL_DETECTORS:
        rows.append(f"| {d.lens} | {d.name} | {d.kind} | {d.stack} | `{d.grep}` |")
    return "\n".join(rows)
