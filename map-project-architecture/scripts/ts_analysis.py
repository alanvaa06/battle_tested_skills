"""TypeScript/JS analysis by regex: source root, units, relative imports, interfaces."""
from __future__ import annotations

import posixpath
import re
from collections import Counter

from scanner import SourceFile

SOURCE_ROOTS = ("src", "app", "lib", "packages")
SOURCE_ROOT_SHARE = 0.7
# Matched against the whole file, so a wrapped `{...}` clause still resolves.
# Only that clause may span lines: letting the rest of the clause cross a
# newline makes every `export` in a semicolon-free file scan to end of file.
IMPORT_RE = re.compile(
    r"""(?:import|export)\s+"""
    r"""(?:(?:[^'";{}\n]*\{[^'";{}]*\})?[^'";{}\n]*?\s+from\s+)?"""
    r"""['"]([^'"]+)['"]"""
    r"""|require\(\s*['"]([^'"]+)['"]\s*\)"""
    r"""|import\(\s*['"]([^'"]+)['"]\s*\)"""
)
COMMENT_STARTS = ("//", "/*", "*")
ALIAS_PREFIXES = ("@/", "~/", "#", "$")
INTERFACE_RE = re.compile(r"^\s*export\s+(?:declare\s+)?interface\s+(\w+)")
ABSTRACT_CLASS_RE = re.compile(r"^\s*export\s+(?:declare\s+)?abstract\s+class\s+(\w+)")
ABSTRACT_MEMBER_RE = re.compile(
    r"^\s*(?:public\s+|protected\s+)?abstract\s+(?:readonly\s+)?(\w+)\s*[(<:]"
)
MEMBER_RE = re.compile(r"^\s*(?:readonly\s+)?(\w+)\s*[(?:<]")
CLASS_RE = re.compile(r"\bclass\s+(\w+)[^{]*?\b(?:implements|extends)\s+([\w\s,<>]+)")


def source_root(files: list[SourceFile]) -> str:
    """The one directory holding most of the sources, or "" for a repo-root layout."""
    ts = [f for f in files if f.stack == "ts"]
    if not ts:
        return ""
    for candidate in SOURCE_ROOTS:
        held = sum(1 for f in ts if f.rel.startswith(candidate + "/"))
        if held > SOURCE_ROOT_SHARE * len(ts):
            return candidate
    return ""


def unit_of(rel: str, root: str) -> str | None:
    prefix = root + "/" if root else ""
    if not rel.startswith(prefix):
        return None
    rest = rel[len(prefix):]
    if "/" in rest:
        return rest.split("/", 1)[0]
    return posixpath.splitext(rest)[0]


def units(files: list[SourceFile], root: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for f in files:
        if f.stack != "ts":
            continue
        u = unit_of(f.rel, root)
        if u is None:
            continue
        rest = f.rel[len(root) + 1:] if root else f.rel
        kind = "package" if "/" in rest else "module"
        entry = out.setdefault(u, {"name": u, "kind": kind, "files": 0, "lines": 0})
        entry["files"] += 1
        entry["lines"] += len(f.lines)
    return out


def import_graph(files: list[SourceFile], root: str) -> dict:
    edges: Counter[tuple[str, str]] = Counter()
    unresolved: list[dict] = []
    for f in files:
        if f.stack != "ts":
            continue
        src = unit_of(f.rel, root)
        if src is None:
            continue
        text = "\n".join(f.lines)
        for m in IMPORT_RE.finditer(text):
            spec = m.group(1) or m.group(2) or m.group(3)
            line_no = text.count("\n", 0, m.start()) + 1
            keyword_line = f.lines[line_no - 1].strip() if line_no <= len(f.lines) else ""
            if keyword_line.startswith(COMMENT_STARTS):
                continue
            if spec.startswith("."):
                target = posixpath.normpath(posixpath.join(posixpath.dirname(f.rel), spec))
                dst = None if target.startswith("..") else unit_of(target, root)
                if dst is None:
                    unresolved.append({"file": f.rel, "line": line_no, "spec": spec})
                elif dst != src:
                    edges[(src, dst)] += 1
            elif spec.startswith(ALIAS_PREFIXES):
                unresolved.append({"file": f.rel, "line": line_no, "spec": spec})
    return {
        "edges": [{"from": a, "to": b, "count": n} for (a, b), n in sorted(edges.items())],
        "unresolved": unresolved,
    }


def _brace_scan(line: str, quote: str) -> tuple[int, bool, str, int]:
    """Net `{`/`}` and `(`/`)` on one line, whether a brace opened, and the
    trailing literal.

    `quote` carries an unterminated literal in from the previous line, which is
    what a multi-line template literal needs. Deliberately approximate: regexes
    and block comments can still fool it, and the cost is a member name lost
    or a scan that ends one declaration late.
    """
    delta = 0
    opened = False
    parens = 0
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = ""
        elif ch in "'\"`":
            quote = ch
        elif line.startswith("//", i):
            break
        elif ch == "{":
            delta += 1
            opened = True
        elif ch == "}":
            delta -= 1
        elif ch == "(":
            parens += 1
        elif ch == ")":
            parens -= 1
        i += 1
    return delta, opened, quote, parens


def _inline_members(line: str, abstract_only: bool) -> list[str]:
    """Members of a declaration whose body opens and closes on its own line."""
    open_at = line.find("{")
    close_at = line.rfind("}")
    if open_at < 0 or close_at < open_at:
        return []
    pattern = ABSTRACT_MEMBER_RE if abstract_only else MEMBER_RE
    names: list[str] = []
    for part in re.split(r"[;,]", line[open_at + 1:close_at]):
        m = pattern.match(part)
        if m:
            names.append(m.group(1))
    return names


def _members(lines: list[str], decl: int, abstract_only: bool) -> list[str]:
    """Member names inside the body opened at or after line index `decl`.

    Brace depth decides where the body ends, so a sibling declaration below it
    -- or an object literal at column 0 -- never donates its own names.
    """
    pattern = ABSTRACT_MEMBER_RE if abstract_only else MEMBER_RE
    names: list[str] = []
    depth = 0
    parens = 0
    quote = ""
    open_line: int | None = None
    for idx in range(decl, len(lines)):
        line = lines[idx]
        # Exactly 1: a field whose own type is an object literal opens a deeper
        # level, and the names inside it belong to that type, not to this one.
        # A continued parameter list is not a member list: `id: string,` on its
        # own line inside `put(...)` is an argument, not a member of the type.
        if open_line is not None and depth == 1 and parens == 0:
            m = pattern.match(line)
            if m:
                names.append(m.group(1))
        delta, opened_here, quote, paren_delta = _brace_scan(line, quote)
        depth += delta
        parens = max(0, parens + paren_delta)
        if open_line is None and opened_here:
            open_line = idx
        if open_line is not None and depth <= 0:
            if idx == open_line:
                return _inline_members(line, abstract_only)
            break
    return names


def contracts(files: list[SourceFile], root: str, edges: list[dict] | None = None) -> list[dict]:
    if edges is None:
        edges = import_graph(files, root)["edges"]
    reachable = {(e["from"], e["to"]) for e in edges}
    declared: list[dict] = []
    implementers: list[dict] = []
    for f in files:
        if f.stack != "ts":
            continue
        unit = unit_of(f.rel, root)
        if unit is None:
            continue
        for i, line in enumerate(f.lines):
            m = INTERFACE_RE.match(line)
            if m:
                declared.append({"name": m.group(1), "kind": "interface", "unit": unit, "file": f.rel,
                                 "line": i + 1, "abstract_methods": _members(f.lines, i, False)})
                continue
            m = ABSTRACT_CLASS_RE.match(line)
            if m:
                declared.append({"name": m.group(1), "kind": "abstract_class", "unit": unit, "file": f.rel,
                                 "line": i + 1, "abstract_methods": _members(f.lines, i, True)})
                continue
            m = CLASS_RE.search(line)
            if m:
                targets = [t.strip().split("<")[0] for t in m.group(2).split(",")]
                implementers.append({"name": m.group(1), "unit": unit, "file": f.rel, "line": i + 1, "targets": targets})
    out: list[dict] = []
    for d in declared:
        impl = [
            {"name": i["name"], "unit": i["unit"], "file": i["file"], "line": i["line"]}
            for i in implementers
            if d["name"] in i["targets"]
            and (i["unit"] == d["unit"] or (i["unit"], d["unit"]) in reachable)
        ]
        out.append({
            "name": d["name"], "kind": d["kind"], "unit": d["unit"],
            "abstract_methods": d["abstract_methods"],
            "implementers": sorted(impl, key=lambda i: (i["unit"], i["name"])),
            "evidence": [{"file": d["file"], "line": d["line"]}],
        })
    return sorted(out, key=lambda c: (c["unit"], c["name"]))
