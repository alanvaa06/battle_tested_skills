"""scanner: walk the repo, read text files, build the meta block."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from scanner import (
    SourceFile,
    _dunder_version,
    _pyproject_name_version,
    _read,
    _roots,
    json_failures,
    meta,
    scan,
)


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
    assert "ts" not in m["languages"]  # node_modules/skipme/index.js was skipped
    assert m["languages"]["py"] == sum(1 for f in files if f.stack == "py")
    assert m["capped"] is False


def test_meta_reads_package_json(ts_repo: Path) -> None:
    files, capped = scan(ts_repo, max_files=1000)
    m = meta(ts_repo, files, capped)
    assert m["name"] == "tsdemo" and m["version"] == "1.2.0"
    assert m["languages"] == {"ts": 4}


def _link_dir(link: Path, target: Path) -> None:
    """Point `link` at directory `target`; skip the test if this machine cannot."""
    try:
        os.symlink(target, link, target_is_directory=True)
        return
    except (OSError, NotImplementedError, AttributeError):
        pass
    try:
        done = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True, text=True, check=False,
        )
    except OSError:
        done = None
    if done is None or done.returncode != 0 or not link.exists():
        pytest.skip("this machine cannot create directory links")


def test_scan_does_not_loop_through_a_directory_link_to_an_ancestor(tmp_path: Path) -> None:
    a = tmp_path / "a"
    (a / "b").mkdir(parents=True)
    (a / "seed.txt").write_text("seed\n", encoding="utf-8")
    _link_dir(a / "b" / "back", a)

    files, capped = scan(tmp_path, max_files=1000)

    assert [f.rel for f in files] == ["a/seed.txt"]
    assert capped is False


def test_scan_splits_lines_without_treating_a_form_feed_as_a_break(tmp_path: Path) -> None:
    (tmp_path / "x.py").write_bytes(b"a\nb\x0cc\nd\n")
    files, _ = scan(tmp_path, max_files=1000)
    assert [f.lines for f in files] == [["a", "b\x0cc", "d"]]


def test_read_rejects_binary_and_oversized_files(tmp_path: Path) -> None:
    binary = tmp_path / "b.bin"
    binary.write_bytes(b"MZ\x00\x00payload")
    assert _read(binary) is None

    huge = tmp_path / "huge.txt"
    huge.write_bytes(b"x" * 2_000_001)
    assert _read(huge) is None

    ok = tmp_path / "ok.txt"
    ok.write_bytes(b"hello\n")
    assert _read(ok) == "hello\n"


def test_roots_keeps_manifest_dirs_and_drops_example_and_fixture_ones() -> None:
    rels = [
        "package.json",
        "packages/api/package.json",
        "examples/demo/package.json",
        "tests/fixtures/py_repo/pyproject.toml",
    ]
    files = [SourceFile(Path("x"), rel, None, []) for rel in rels]
    assert _roots(files) == [".", "packages/api"]


def test_pyproject_name_version_reads_a_poetry_manifest() -> None:
    lines = ["[tool.poetry]", 'name = "demo"', 'version = "0.1.0"']
    assert _pyproject_name_version(lines) == ("demo", "0.1.0")


def test_pyproject_name_version_prefers_project_over_poetry() -> None:
    lines = [
        "[project]",
        'name = "a"',
        'version = "1.0.0"',
        "[tool.poetry]",
        'name = "b"',
        'version = "2.0.0"',
    ]
    assert _pyproject_name_version(lines) == ("a", "1.0.0")


def test_a_byte_order_mark_never_reaches_line_one(tmp_path: Path) -> None:
    (tmp_path / "m.py").write_bytes(b"\xef\xbb\xbfimport sqlalchemy\n")
    files, _ = scan(tmp_path, max_files=10)
    assert files[0].lines[0] == "import sqlalchemy"


def test_json_failures_names_the_file_and_the_line(tmp_path: Path) -> None:
    (tmp_path / "good.json").write_text('{"a": 1}', encoding="utf-8")
    (tmp_path / "package.json").write_text('{\n  "a": 1,\n}\n', encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    assert json_failures(files) == [{"kind": "json_parse_failure", "file": "package.json", "line": 2}]


def test_a_jsonc_config_this_tool_never_parses_is_not_flagged(tmp_path: Path) -> None:
    # tsconfig.json legitimately allows `//` comments; nothing in the inventory
    # parses it, so it must not be reported as a JSON parse failure either.
    (tmp_path / "tsconfig.json").write_text(
        '{\n  // strict mode\n  "compilerOptions": {"strict": true}\n}\n', encoding="utf-8"
    )
    files, _ = scan(tmp_path, max_files=10)
    assert json_failures(files) == []


def test_a_broken_consumed_config_is_still_flagged(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{\n  "a": 1,\n', encoding="utf-8")
    (tmp_path / ".mcp.json").write_text('{"mcpServers": {}\n', encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    assert {r["file"] for r in json_failures(files)} == {"package.json", ".mcp.json"}


def test_dunder_version_prefers_the_shallowest_init() -> None:
    files = [
        SourceFile(Path("x"), "src/demo/deep/nested/__init__.py", "py", ['__version__ = "9.9.9"']),
        SourceFile(Path("x"), "src/demo/__init__.py", "py", ['__version__ = "0.1.0"']),
    ]
    assert _dunder_version(files) == "0.1.0"
