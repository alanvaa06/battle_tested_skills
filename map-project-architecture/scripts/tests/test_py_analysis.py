"""py_analysis: package discovery, units, import graph, contracts (ast-based)."""
# Line numbers below are asserted against the fixture files; editing a fixture shifts them.
from __future__ import annotations

from pathlib import Path

import pytest

from py_analysis import contracts, import_graph, other_top_packages, project_package, units
from scanner import scan

REFERENCE_REPO = Path(r"C:\Proyectos\S_Portfolio-Construction")


@pytest.fixture
def py_files(py_repo: Path):
    files, _ = scan(py_repo, max_files=1000)
    return files


def _write(root: Path, rel: str, text: str = "") -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _scan(root: Path):
    files, _ = scan(root, max_files=1000)
    return files


def test_project_package_is_the_one_with_children(py_files) -> None:
    assert project_package(py_files) == ("src/demo", "demo")


def test_project_package_ignores_test_packages(tmp_path: Path) -> None:
    for rel in ("tests/a/__init__.py", "tests/b/__init__.py", "src/pkg/__init__.py",
                "src/pkg/x/__init__.py", "src/pkg/y/__init__.py"):
        _write(tmp_path, rel)
    assert project_package(_scan(tmp_path)) == ("src/pkg", "pkg")


def test_project_package_without_children_still_skips_tests(tmp_path: Path) -> None:
    for rel in ("tests/a/__init__.py", "tests/b/__init__.py", "src/pkg/__init__.py"):
        _write(tmp_path, rel)
    assert project_package(_scan(tmp_path)) == ("src/pkg", "pkg")


def test_project_package_skips_a_docs_package_with_children(tmp_path: Path) -> None:
    for rel in ("docs/pkg/__init__.py", "docs/pkg/x/__init__.py", "docs/pkg/y/__init__.py",
                "src/pkg/__init__.py", "src/pkg/x/__init__.py"):
        _write(tmp_path, rel)
    assert project_package(_scan(tmp_path)) == ("src/pkg", "pkg")


def test_project_package_prefers_src_at_equal_depth(tmp_path: Path) -> None:
    for rel in ("app/pkg/__init__.py", "app/pkg/x/__init__.py", "app/pkg/y/__init__.py",
                "src/core/__init__.py", "src/core/x/__init__.py", "src/core/y/__init__.py"):
        _write(tmp_path, rel)
    assert project_package(_scan(tmp_path)) == ("src/core", "core")


def test_other_top_packages_lists_the_disjoint_survivors(tmp_path: Path) -> None:
    for rel in ("app/pkg/__init__.py", "app/pkg/x/__init__.py", "app/pkg/y/__init__.py",
                "src/core/__init__.py", "src/core/x/__init__.py", "src/core/y/__init__.py",
                "tests/a/__init__.py"):
        _write(tmp_path, rel)
    assert other_top_packages(_scan(tmp_path), "src/core") == ["app/pkg"]


@pytest.mark.skipif(not REFERENCE_REPO.is_dir(), reason="reference repo absent")
def test_project_package_on_the_reference_repo() -> None:
    files, _ = scan(REFERENCE_REPO, max_files=20000)
    assert project_package(files) == (
        "src/kaxanuk/portfolio_construction",
        "kaxanuk.portfolio_construction",
    )


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


def _demo_repo(tmp_path: Path, cli_body: str) -> list:
    _write(tmp_path, "src/demo/__init__.py")
    _write(tmp_path, "src/demo/db/__init__.py")
    _write(tmp_path, "src/demo/cli.py", cli_body)
    return _scan(tmp_path)


def test_from_package_import_unit_makes_an_edge(tmp_path: Path) -> None:
    g = import_graph(_demo_repo(tmp_path, "from demo import db\n"), "src/demo", "demo")
    assert [(e["from"], e["to"]) for e in g["edges"]] == [("cli", "db")]


def test_from_package_import_of_a_non_unit_is_dropped(tmp_path: Path) -> None:
    g = import_graph(_demo_repo(tmp_path, "from demo import VERSION, db\n"), "src/demo", "demo")
    assert [(e["from"], e["to"]) for e in g["edges"]] == [("cli", "db")]
    assert "VERSION" not in {n for e in g["edges"] for n in (e["from"], e["to"])}


def test_type_checking_imports_are_skipped_but_local_ones_are_not(tmp_path: Path) -> None:
    _write(tmp_path, "src/demo/__init__.py")
    _write(tmp_path, "src/demo/db/__init__.py")
    _write(tmp_path, "src/demo/api/__init__.py")
    _write(tmp_path, "src/demo/cli.py",
           "from typing import TYPE_CHECKING\n"
           "\n"
           "if TYPE_CHECKING:\n"
           "    from demo.db import pg\n"
           "\n"
           "\n"
           "def go():\n"
           "    from demo.api import client\n"
           "    return client\n")
    g = import_graph(_scan(tmp_path), "src/demo", "demo")
    assert [(e["from"], e["to"]) for e in g["edges"]] == [("cli", "api")]


def test_contracts_find_abc_and_implementers(py_files) -> None:
    cs = contracts(py_files, "src/demo")
    assert len(cs) == 1
    c = cs[0]
    assert c["name"] == "Repo" and c["kind"] == "abc" and c["unit"] == "core"
    assert c["abstract_methods"] == ["get"]
    assert c["implementers"] == [{"name": "PgRepo", "unit": "db", "file": "src/demo/db/pg.py", "line": 6}]
    assert c["evidence"] == [{"file": "src/demo/core/base.py", "line": 4}]


def test_cross_unit_implementers_need_an_import_edge(tmp_path: Path) -> None:
    _write(tmp_path, "src/demo/__init__.py")
    _write(tmp_path, "src/demo/core/__init__.py")
    _write(tmp_path, "src/demo/core/base.py",
           "from abc import ABC, abstractmethod\n"
           "\n"
           "\n"
           "class Base(ABC):\n"
           "    @abstractmethod\n"
           "    def get(self) -> str: ...\n")
    _write(tmp_path, "src/demo/db/__init__.py")
    _write(tmp_path, "src/demo/db/other.py",
           "class Base:\n"
           "    pass\n"
           "\n"
           "\n"
           "class Impl(Base):\n"
           "    pass\n")
    cs = contracts(_scan(tmp_path), "src/demo")
    assert [(c["name"], c["unit"]) for c in cs] == [("Base", "core")]
    assert cs[0]["implementers"] == []
