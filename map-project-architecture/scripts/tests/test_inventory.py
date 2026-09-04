"""inventory: orchestration and CLI."""
from __future__ import annotations

import json
import time
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


def test_a_corrupt_previous_inventory_never_aborts_the_run(py_repo: Path, tmp_path: Path, capsys) -> None:
    previous = tmp_path / "old.json"
    previous.write_text("{not json", encoding="utf-8")
    out = tmp_path / "inv.json"
    assert main([str(py_repo), "--out", str(out), "--diff", str(previous)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["meta"]["name"] == "demo"
    printed = capsys.readouterr().out
    assert "[!] cannot diff" in printed and str(previous) in printed


def test_a_previous_inventory_of_another_schema_is_reported(py_repo: Path, tmp_path: Path, capsys) -> None:
    previous = tmp_path / "old.json"
    previous.write_text(json.dumps({"schema": 0}), encoding="utf-8")
    out = tmp_path / "inv.json"
    assert main([str(py_repo), "--out", str(out), "--diff", str(previous)]) == 0
    assert out.is_file()
    assert "[!] cannot diff" in capsys.readouterr().out


def test_a_valid_previous_inventory_is_diffed(py_repo: Path, tmp_path: Path, capsys) -> None:
    previous = tmp_path / "old.json"
    assert main([str(py_repo), "--out", str(previous)]) == 0
    capsys.readouterr()
    out = tmp_path / "inv.json"
    assert main([str(py_repo), "--out", str(out), "--diff", str(previous)]) == 0
    assert "[diff] against" in capsys.readouterr().out


def test_generated_at_is_utc(py_repo: Path) -> None:
    stamp = build(py_repo, max_files=1000)["generated_at"]
    assert stamp.endswith("Z")
    time.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")


def test_the_out_file_is_excluded_from_the_scan(tmp_path: Path, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text("x = 1\n", encoding="utf-8")
    out = repo / "inventory.json"
    assert main([str(repo), "--out", str(out)]) == 0
    first = json.loads(out.read_text(encoding="utf-8"))["meta"]["files"]
    assert main([str(repo), "--out", str(out)]) == 0
    second = json.loads(out.read_text(encoding="utf-8"))["meta"]["files"]
    assert first == second == 1


def test_max_files_must_be_positive(py_repo: Path, tmp_path: Path, capsys) -> None:
    out = tmp_path / "inv.json"
    assert main([str(py_repo), "--out", str(out), "--max-files", "0"]) == 2
    assert "[x] --max-files must be >= 1" in capsys.readouterr().out
    assert not out.exists()


def test_a_previous_inventory_that_is_not_an_object_is_reported(py_repo: Path, tmp_path: Path, capsys) -> None:
    previous = tmp_path / "old.json"
    previous.write_text("[]", encoding="utf-8")
    out = tmp_path / "inv.json"
    assert main([str(py_repo), "--out", str(out), "--diff", str(previous)]) == 0
    assert out.is_file()
    assert "[!] cannot diff" in capsys.readouterr().out


def test_a_broken_json_file_is_reported_as_unresolved(tmp_path: Path) -> None:
    # package.json is a file this tool actually consumes, so a parse failure
    # in it belongs in `unresolved` (an arbitrary *.json would not, since
    # json_failures only inspects files the inventory reads).
    (tmp_path / "m.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "package.json").write_text("{\n  oops\n}\n", encoding="utf-8")
    inv = build(tmp_path, max_files=10)
    assert {"kind": "json_parse_failure", "file": "package.json", "line": 2} in inv["unresolved"]
