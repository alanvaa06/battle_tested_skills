"""Python analysis via ast: project package, units, import graph, contracts."""
from __future__ import annotations

import ast
import posixpath
from collections import Counter

from scanner import NON_ROOT_SEGMENTS, SourceFile


def _dirname(rel: str) -> str:
    return posixpath.dirname(rel)


def _module_path(dir_rel: str) -> str:
    parts = dir_rel.split("/")
    if parts and parts[0] == "src":
        parts = parts[1:]
    return ".".join(parts)


def _within(child: str, parent: str) -> bool:
    return child.startswith(parent + "/")


def _candidate_dirs(files: list[SourceFile]) -> list[str]:
    """Package dirs that could be the project's own, shallowest first, src/ first.

    A package under tests/, docs/ or fixtures/ is somebody else's tree: it is
    often shallower and wider than the real one, and picking it would put every
    later unit, edge and contract in the wrong package.
    """
    dirs = {
        d for d in (_dirname(f.rel) for f in files
                    if f.rel.endswith("__init__.py") and "/" in f.rel)
        if not NON_ROOT_SEGMENTS.intersection(d.split("/"))
    }
    return sorted(dirs, key=lambda d: (d.count("/"), 0 if d.split("/")[0] == "src" else 1, d))


def project_package(files: list[SourceFile]) -> tuple[str, str] | None:
    """(dir, module) of the shallowest package with >= 2 child packages, else the shallowest package."""
    pkg_dirs = _candidate_dirs(files)
    if not pkg_dirs:
        return None
    for d in pkg_dirs:
        children = [c for c in pkg_dirs if _dirname(c) == d]
        if len(children) >= 2:
            return d, _module_path(d)
    return pkg_dirs[0], _module_path(pkg_dirs[0])


def other_top_packages(files: list[SourceFile], chosen_dir: str) -> list[str]:
    """Candidate packages the chosen one neither contains nor sits inside.

    A second top-level package means this repo holds more than the analysis
    describes; the caller reports them rather than silently dropping them.
    """
    disjoint = [
        d for d in _candidate_dirs(files)
        if d != chosen_dir and not _within(d, chosen_dir) and not _within(chosen_dir, d)
    ]
    return sorted(d for d in disjoint if not any(_within(d, o) for o in disjoint))


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


def _resolve_from(node: ast.ImportFrom, module: str, is_init: bool, pkg_module: str) -> list[str]:
    if node.level == 0:
        base = node.module or ""
    else:
        pkg = module if is_init else module.rsplit(".", 1)[0]
        for _ in range(node.level - 1):
            pkg = pkg.rsplit(".", 1)[0] if "." in pkg else ""
        base = pkg + ("." + node.module if node.module else "")
    # `from pkg import unit` names the unit in the alias, not in the module.
    if node.module is None or base == pkg_module:
        return [f"{base}.{alias.name}" for alias in node.names]
    return [base]


def _is_type_checking(test: ast.expr) -> bool:
    return (
        (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING")
        or (isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")
    )


def _import_nodes(tree: ast.Module):
    """Every Import/ImportFrom that runs, so function-local imports count and
    `if TYPE_CHECKING:` bodies (which never execute) do not."""
    stack = list(ast.iter_child_nodes(tree))
    while stack:
        node = stack.pop()
        if isinstance(node, ast.If) and _is_type_checking(node.test):
            stack.extend(node.orelse)
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            yield node
            continue
        stack.extend(ast.iter_child_nodes(node))


def _parse_all(files: list[SourceFile], pkg_dir: str) -> tuple[dict[str, ast.Module], list[dict]]:
    """Parse every in-package Python file once; report the ones that would not parse."""
    trees: dict[str, ast.Module] = {}
    failures: list[dict] = []
    for f in files:
        if f.stack != "py" or unit_of(f.rel, pkg_dir) is None:
            continue
        try:
            trees[f.rel] = ast.parse("\n".join(f.lines))
        except SyntaxError as exc:
            failures.append({"file": f.rel, "line": exc.lineno or 0})
    return trees, failures


def import_graph(
    files: list[SourceFile],
    pkg_dir: str,
    pkg_module: str,
    unit_names: set[str] | None = None,
) -> dict:
    if unit_names is None:
        unit_names = set(units(files, pkg_dir))
    trees, failures = _parse_all(files, pkg_dir)
    edges: Counter[tuple[str, str]] = Counter()
    for rel, tree in trees.items():
        src = unit_of(rel, pkg_dir)
        module, is_init = _file_module(rel, pkg_dir, pkg_module)
        for node in _import_nodes(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            else:
                names = _resolve_from(node, module, is_init, pkg_module)
            for name in names:
                if not name.startswith(pkg_module + "."):
                    continue
                dst = name[len(pkg_module) + 1:].split(".", 1)[0]
                # An unknown target is a class or constant re-exported by the
                # package, not a unit: an edge to it would invent a box.
                if dst != src and dst in unit_names:
                    edges[(src, dst)] += 1
    return {
        "edges": [{"from": a, "to": b, "count": n} for (a, b), n in sorted(edges.items())],
        "parse_failures": failures,
    }


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


def contracts(files: list[SourceFile], pkg_dir: str, edges: list[dict] | None = None) -> list[dict]:
    if edges is None:
        edges = import_graph(files, pkg_dir, _module_path(pkg_dir))["edges"]
    reachable = {(e["from"], e["to"]) for e in edges}
    trees, _ = _parse_all(files, pkg_dir)
    classes: list[dict] = []
    for rel, tree in trees.items():
        unit = unit_of(rel, pkg_dir)
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
                "name": node.name, "bases": bases, "unit": unit, "file": rel,
                "line": node.lineno, "abstract_methods": abstract, "kind": kind,
            })
    out: list[dict] = []
    for c in classes:
        if c["kind"] is None:
            continue
        # A bare base name repeats across units; only an import makes it the same class.
        implementers = [
            {"name": o["name"], "unit": o["unit"], "file": o["file"], "line": o["line"]}
            for o in classes
            if c["name"] in o["bases"]
            and (o["unit"] == c["unit"] or (o["unit"], c["unit"]) in reachable)
        ]
        out.append({
            "name": c["name"], "kind": c["kind"], "unit": c["unit"],
            "abstract_methods": c["abstract_methods"],
            "implementers": sorted(implementers, key=lambda i: (i["unit"], i["name"])),
            "evidence": [{"file": c["file"], "line": c["line"]}],
        })
    return sorted(out, key=lambda c: (c["unit"], c["name"]))
