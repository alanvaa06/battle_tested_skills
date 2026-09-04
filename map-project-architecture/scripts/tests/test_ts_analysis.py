"""ts_analysis: source root, units, relative-import graph, interfaces."""
# Line numbers below are asserted against the fixture files; editing a fixture shifts them.
from __future__ import annotations

from pathlib import Path

import pytest

from scanner import scan
from ts_analysis import contracts, import_graph, source_root, units


@pytest.fixture
def ts_files(ts_repo: Path):
    files, _ = scan(ts_repo, max_files=1000)
    return files


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _scan(root: Path):
    files, _ = scan(root, max_files=1000)
    return files


def test_source_root_is_src(ts_files) -> None:
    assert source_root(ts_files) == "src"


def test_source_root_is_empty_when_no_dir_dominates(tmp_path: Path) -> None:
    for rel in ("app/page.tsx", "components/x.tsx", "lib/y.ts", "hooks/z.ts"):
        _write(tmp_path, rel, "export const v = 1;\n")
    files = _scan(tmp_path)
    assert source_root(files) == ""
    assert set(units(files, "")) == {"app", "components", "hooks", "lib"}


def test_units_are_first_dirs_under_root(ts_files) -> None:
    u = units(ts_files, "src")
    assert sorted(u) == ["app", "lib", "services"]
    assert u["lib"]["files"] == 2


def test_import_graph_resolves_relative_only(ts_files) -> None:
    g = import_graph(ts_files, "src")
    edges = {(e["from"], e["to"]): e["count"] for e in g["edges"]}
    assert edges == {("services", "lib"): 2, ("app", "services"): 1}
    assert g["unresolved"] == []


def test_alias_imports_are_reported_unresolved(tmp_path: Path) -> None:
    (tmp_path / "src" / "a").mkdir(parents=True)
    (tmp_path / "src" / "a" / "x.ts").write_text("import { y } from '@/b/y';\n", encoding="utf-8")
    files, _ = scan(tmp_path, max_files=100)
    g = import_graph(files, "src")
    assert g["edges"] == []
    assert g["unresolved"] == [{"file": "src/a/x.ts", "line": 1, "spec": "@/b/y"}]


def _graph_of(tmp_path: Path, x_body: str) -> dict:
    _write(tmp_path, "src/b/y.ts", "export const y = 1;\nexport const z = 2;\n")
    _write(tmp_path, "src/a/x.ts", x_body)
    return import_graph(_scan(tmp_path), "src")


def test_multi_line_import_makes_an_edge(tmp_path: Path) -> None:
    g = _graph_of(tmp_path, "import {\n  y,\n  z\n} from '../b/y';\n")
    assert [(e["from"], e["to"]) for e in g["edges"]] == [("a", "b")]
    assert g["unresolved"] == []


def test_commented_import_is_ignored(tmp_path: Path) -> None:
    g = _graph_of(tmp_path, "// import { y } from '../b/y';\n")
    assert g["edges"] == []
    assert g["unresolved"] == []


def test_dynamic_import_makes_an_edge(tmp_path: Path) -> None:
    g = _graph_of(tmp_path, "const m = await import('../b/y');\n")
    assert [(e["from"], e["to"]) for e in g["edges"]] == [("a", "b")]


def test_relative_import_outside_the_root_is_unresolved(tmp_path: Path) -> None:
    _write(tmp_path, "vendor/z.ts", "export const z = 1;\n")
    _write(tmp_path, "src/a/x.ts", "import { z } from '../../vendor/z';\n")
    _write(tmp_path, "src/a/w.ts", "export const w = 1;\n")
    _write(tmp_path, "src/b/y.ts", "export const y = 1;\n")
    g = import_graph(_scan(tmp_path), "src")
    assert g["edges"] == []
    assert g["unresolved"] == [{"file": "src/a/x.ts", "line": 1, "spec": "../../vendor/z"}]


def test_contracts_find_interface_and_implementers(ts_files) -> None:
    cs = contracts(ts_files, "src")
    assert len(cs) == 1
    c = cs[0]
    assert c["name"] == "Store" and c["kind"] == "interface" and c["unit"] == "lib"
    assert c["abstract_methods"] == ["get", "put"]
    assert c["implementers"] == [{"name": "MemoryStore", "unit": "services", "file": "src/services/user.ts", "line": 11}]


def test_members_stop_at_the_declaration_brace(tmp_path: Path) -> None:
    _write(tmp_path, "src/lib/t.ts",
           "export interface A { a: string }\n"
           "\n"
           "export const CONFIG = {\n"
           "  host: 1,\n"
           "};\n")
    cs = contracts(_scan(tmp_path), "src")
    assert [c["name"] for c in cs] == ["A"]
    assert cs[0]["abstract_methods"] == ["a"]


def test_namespaced_interfaces_keep_their_own_members(tmp_path: Path) -> None:
    _write(tmp_path, "src/lib/n.ts",
           "export namespace N {\n"
           "  export interface A {\n"
           "    a(): void;\n"
           "  }\n"
           "  export interface B {\n"
           "    b(): void;\n"
           "  }\n"
           "}\n")
    cs = contracts(_scan(tmp_path), "src")
    assert {c["name"]: c["abstract_methods"] for c in cs} == {"A": ["a"], "B": ["b"]}


def test_abstract_readonly_member_is_named(tmp_path: Path) -> None:
    _write(tmp_path, "src/lib/c.ts",
           "export abstract class C {\n"
           "  abstract readonly id: string;\n"
           "  abstract run(): void;\n"
           "}\n")
    cs = contracts(_scan(tmp_path), "src")
    assert cs[0]["abstract_methods"] == ["id", "run"]


def test_cross_unit_implementers_need_an_import_edge(tmp_path: Path) -> None:
    _write(tmp_path, "src/lib/types.ts", "export interface Store {\n  get(): void;\n}\n")
    _write(tmp_path, "src/services/user.ts",
           "interface Store { other(): void }\n"
           "export class MemoryStore implements Store {\n"
           "  other(): void {}\n"
           "}\n")
    cs = contracts(_scan(tmp_path), "src")
    store = next(c for c in cs if c["unit"] == "lib")
    assert store["implementers"] == []


def test_nested_object_fields_do_not_leak_into_members(tmp_path: Path) -> None:
    _write(tmp_path, "src/a/i.ts", (
        "export interface E {\n"
        "  a: {\n"
        "    nested: string;\n"
        "  };\n"
        "  c: number;\n"
        "}\n"
    ))
    files, _ = scan(tmp_path, max_files=10)
    c = contracts(files, "src")
    assert [x["name"] for x in c] == ["E"]
    assert c[0]["abstract_methods"] == ["a", "c"]


def test_a_block_comment_line_is_not_an_import(tmp_path: Path) -> None:
    _write(tmp_path, "src/a/i.ts", "/* import { x } from '../b/i'; */\nexport const y = 1;\n")
    _write(tmp_path, "src/b/i.ts", "export const x = 1;\n")
    files, _ = scan(tmp_path, max_files=10)
    assert import_graph(files, "src")["edges"] == []


def test_multi_line_method_parameters_are_not_members(tmp_path: Path) -> None:
    _write(tmp_path, "src/lib/s.ts", (
        "export interface Store {\n"
        "  get(id: string): string;\n"
        "  put(\n"
        "    id: string,\n"
        "    value: string\n"
        "  ): void;\n"
        "}\n"
    ))
    cs = contracts(_scan(tmp_path), "src")
    assert cs[0]["abstract_methods"] == ["get", "put"]
