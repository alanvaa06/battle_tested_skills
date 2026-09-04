"""entrypoints: ranked list of the ways a user or process enters the repo."""
from __future__ import annotations

from pathlib import Path

import pytest

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


REFERENCE_REPO = Path("C:/Proyectos/S_Portfolio-Construction")


def test_quoted_project_scripts_key_is_read(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\n'
        'name = "kn"\n'
        '\n'
        '[project.scripts]\n'
        '"kaxanuk.portfolio_construction" = "kaxanuk.portfolio_construction:cli"\n',
        encoding="utf-8",
    )
    files, _ = scan(tmp_path, max_files=10)
    e = entrypoints(files)
    assert _kinds(e) == [("project.scripts", "kaxanuk.portfolio_construction")]
    assert e[0]["target"] == "kaxanuk.portfolio_construction:cli"
    assert e[0]["evidence"] == [{"file": "pyproject.toml", "line": 5}]


@pytest.mark.skipif(not REFERENCE_REPO.is_dir(), reason="reference repo not present")
def test_reference_repo_leads_with_its_project_script() -> None:
    files, _ = scan(REFERENCE_REPO, max_files=20000)
    assert entrypoints(files)[0]["kind"] == "project.scripts"


def test_package_json_evidence_line_sits_in_its_own_section(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        '{\n'
        '  "name": "x",\n'
        '  "bin": {\n'
        '    "build": "./b.js"\n'
        '  },\n'
        '  "scripts": {\n'
        '    "build": "tsc"\n'
        '  }\n'
        '}\n',
        encoding="utf-8",
    )
    files, _ = scan(tmp_path, max_files=10)
    e = {(x["kind"], x["name"]): x for x in entrypoints(files)}
    assert e[("bin", "build")]["evidence"] == [{"file": "package.json", "line": 4}]
    assert e[("npm_script", "build")]["evidence"] == [{"file": "package.json", "line": 7}]


def test_cli_framework_needs_a_cli_name_or_a_main_guard(tmp_path: Path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_cli.py").write_text("from click.testing import CliRunner\n", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    assert [k for k, _ in _kinds(entrypoints(files))] == []

    (tmp_path / "run.py").write_text(
        "import argparse\n\nif __name__ == '__main__':\n    pass\n", encoding="utf-8"
    )
    files, _ = scan(tmp_path, max_files=10)
    assert ("cli_framework", "run.py") in _kinds(entrypoints(files))


def test_notebooks_entry_has_a_stable_name_and_a_count(tmp_path: Path) -> None:
    (tmp_path / "a.ipynb").write_text("{}", encoding="utf-8")
    (tmp_path / "b.ipynb").write_text("{}", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    assert entrypoints(files) == [{
        "kind": "notebooks", "name": "notebooks", "target": None, "rank": 10,
        "evidence": [{"file": "a.ipynb", "line": 1}], "count": 2,
    }]


def test_a_string_bin_points_at_the_bin_key_not_a_dependency(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        '{\n'
        '  "name": "cli",\n'
        '  "bin": "./x.js",\n'
        '  "scripts": {\n'
        '    "a": "b"\n'
        '  },\n'
        '  "dependencies": {\n'
        '    "cli": "^1.0.0"\n'
        '  }\n'
        '}\n',
        encoding="utf-8",
    )
    files, _ = scan(tmp_path, max_files=10)
    e = {(x["kind"], x["name"]): x for x in entrypoints(files)}
    assert e[("bin", "cli")]["target"] == "./x.js"
    assert e[("bin", "cli")]["evidence"] == [{"file": "package.json", "line": 3}]


def test_examples_dir_evidence_names_the_first_file_in_it(tmp_path: Path) -> None:
    d = tmp_path / "examples"
    d.mkdir()
    (d / "b_second.py").write_text("x = 1\n", encoding="utf-8")
    (d / "a_first.py").write_text("x = 1\n", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=10)
    e = next(x for x in entrypoints(files) if x["kind"] == "examples_dir")
    assert e["evidence"] == [{"file": "examples/a_first.py", "line": 1}]


def test_a_package_json_with_a_bom_still_parses(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_bytes(
        b'\xef\xbb\xbf{\n  "name": "x",\n  "scripts": {\n    "dev": "vite"\n  }\n}\n'
    )
    files, _ = scan(tmp_path, max_files=10)
    e = {(x["kind"], x["name"]): x for x in entrypoints(files)}
    assert e[("npm_script", "dev")]["target"] == "vite"


def test_evidence_never_points_at_line_zero(tmp_path: Path) -> None:
    # The JSON escape parses to `dev`, so the literal needle is nowhere in the
    # file. Line 0 does not exist; the section's own line is the fallback.
    esc = chr(92) + "u0064ev"
    (tmp_path / "package.json").write_text(
        "{\n"
        '  "name": "x",\n'
        '  "scripts": {\n'
        f'    "{esc}": "vite"\n'
        "  }\n"
        "}\n",
        encoding="utf-8",
    )
    files, _ = scan(tmp_path, max_files=10)
    e = {(x["kind"], x["name"]): x for x in entrypoints(files)}
    assert e[("npm_script", "dev")]["evidence"] == [{"file": "package.json", "line": 3}]
