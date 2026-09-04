"""matches: detector hits, env var reads, URL literals, migration dirs, MCP configs."""
from __future__ import annotations

from pathlib import Path

from matches import EVIDENCE_CAP, matches
from scanner import scan


def test_python_repo_matches(py_repo: Path) -> None:
    files, _ = scan(py_repo, max_files=1000)
    m = matches(files)
    storage = {s["detector"]: s for s in m["storage"]}
    assert set(storage) == {"sqlalchemy"}
    assert storage["sqlalchemy"]["evidence"] == [{"file": "src/demo/db/pg.py", "line": 1}]
    assert [e["detector"] for e in m["external"]] == ["requests"]
    assert m["env"] == {
        "API_KEY": {"count": 1, "evidence": [{"file": "src/demo/api/client.py", "line": 9}]}
    }
    assert m["urls"] == [{
        "url": "https://api.example.com/v1", "count": 1,
        "evidence": [{"file": "src/demo/api/client.py", "line": 5}],
    }]
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


def test_mcp_configs_under_tests_or_fixtures_are_ignored(tmp_path: Path) -> None:
    nested = tmp_path / "tests" / "fixtures"
    nested.mkdir(parents=True)
    (nested / ".mcp.json").write_text('{"mcpServers": {"fake": {}}}', encoding="utf-8")
    (tmp_path / ".mcp.json").write_text('{"mcpServers": {"github": {}}}', encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    assert matches(files)["mcp"] == [{"file": ".mcp.json", "servers": ["github"]}]


def test_env_evidence_is_capped(tmp_path: Path) -> None:
    body = "".join(f'os.environ["API_KEY"]  # {i}\n' for i in range(EVIDENCE_CAP + 5))
    (tmp_path / "m.py").write_text(body, encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    entry = matches(files)["env"]["API_KEY"]
    assert len(entry["evidence"]) == EVIDENCE_CAP
    assert entry["count"] == EVIDENCE_CAP + 5


def test_a_bom_does_not_hide_a_first_line_import(tmp_path: Path) -> None:
    (tmp_path / "m.py").write_bytes(b"\xef\xbb\xbfimport sqlalchemy\n")
    files, _ = scan(tmp_path, max_files=10)
    assert matches(files)["storage"] == [{
        "detector": "sqlalchemy", "lens": "storage", "kind": "sql", "stack": "py",
        "count": 1, "evidence": [{"file": "m.py", "line": 1}],
    }]


def test_migration_dirs_are_found_at_any_depth(tmp_path: Path) -> None:
    d = tmp_path / "myapp" / "migrations"
    d.mkdir(parents=True)
    (d / "0001.py").write_text("x = 1\n", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    assert matches(files)["migrations"] == ["myapp/migrations"]


def test_url_entries_carry_a_count(tmp_path: Path) -> None:
    (tmp_path / "m.py").write_text(
        'a = "https://api.example.com/v1"\n'
        'b = "https://api.example.com/v1"\n',
        encoding="utf-8",
    )
    files, _ = scan(tmp_path, max_files=10)
    assert matches(files)["urls"] == [{
        "url": "https://api.example.com/v1", "count": 2,
        "evidence": [{"file": "m.py", "line": 1}, {"file": "m.py", "line": 2}],
    }]


def test_a_two_segment_migration_dir_is_reported_in_full(tmp_path: Path) -> None:
    d = tmp_path / "apps" / "web" / "prisma" / "migrations"
    d.mkdir(parents=True)
    (d / "0001_init.sql").write_text("select 1;\n", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    assert matches(files)["migrations"] == ["apps/web/prisma/migrations"]


def test_a_migration_dir_under_a_fixtures_tree_is_not_this_repos_migration(tmp_path: Path) -> None:
    d = tmp_path / "tests" / "fixtures" / "py_repo" / "alembic"
    d.mkdir(parents=True)
    (d / "env.py").write_text("x = 1\n", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    assert matches(files)["migrations"] == []


def test_a_migration_dir_outside_any_non_root_segment_is_still_found(tmp_path: Path) -> None:
    d = tmp_path / "db" / "alembic"
    d.mkdir(parents=True)
    (d / "env.py").write_text("x = 1\n", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    assert matches(files)["migrations"] == ["db/alembic"]
