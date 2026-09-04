"""Build inventory.json for a repository. Stdlib only. ASCII-only stdout.

Usage: python inventory.py <repo-root> --out <path/to/inventory.json> [--max-files N]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import py_analysis
import ts_analysis
from detectors import MAX_FILES_DEFAULT
from diff import diff, render
from entrypoints import entrypoints
from graph import layers
from infra import infra
from matches import matches
from scanner import json_failures, meta, scan

SCHEMA_VERSION = 1


def build(root: Path, max_files: int = MAX_FILES_DEFAULT, exclude: Path | None = None) -> dict:
    """Inventory `root`. `exclude` is one resolved path to leave out of the scan --
    the output file itself, when it is written inside the repository being mapped."""
    started = time.time()
    files, capped = scan(root, max_files)
    if exclude is not None:
        files = [f for f in files if f.path.resolve() != exclude]
    unresolved: list[dict] = []

    python = None
    pkg = py_analysis.project_package(files)
    if pkg is not None:
        pkg_dir, module = pkg
        u = py_analysis.units(files, pkg_dir)
        g = py_analysis.import_graph(files, pkg_dir, module, set(u))
        unresolved.extend({"kind": "py_parse_failure", **x} for x in g["parse_failures"])
        unresolved.extend(
            {"kind": "py_other_top_package", "file": d, "line": 0}
            for d in py_analysis.other_top_packages(files, pkg_dir)
        )
        python = {
            "package_dir": pkg_dir, "module": module,
            "units": [u[k] for k in sorted(u)],
            "import_graph": g["edges"],
            "layers": layers(sorted(u), g["edges"]),
            "contracts": py_analysis.contracts(files, pkg_dir, g["edges"]),
        }

    ts = None
    if any(f.stack == "ts" for f in files):
        root_dir = ts_analysis.source_root(files)
        u = ts_analysis.units(files, root_dir)
        g = ts_analysis.import_graph(files, root_dir)
        unresolved.extend({"kind": "ts_alias_import", **x} for x in g["unresolved"])
        ts = {
            "source_root": root_dir,
            "units": [u[k] for k in sorted(u)],
            "import_graph": g["edges"],
            "layers": layers(sorted(u), g["edges"]),
            "contracts": ts_analysis.contracts(files, root_dir, g["edges"]),
        }

    # Every config reader swallows its own parse error to stay useful; this is
    # the one place the unreadable file gets named instead of silently skipped.
    unresolved.extend(json_failures(files))

    m = matches(files)
    return {
        "schema": SCHEMA_VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_s": round(time.time() - started, 2),
        "meta": meta(root, files, capped),
        "code": {"python": python, "ts": ts},
        "storage": m["storage"],
        "migrations": m["migrations"],
        "external": m["external"],
        "env": m["env"],
        "urls": m["urls"],
        "mcp": m["mcp"],
        "entrypoints": entrypoints(files),
        "infra": infra(files),
        "unresolved": unresolved,
    }


def summary(inv: dict) -> list[str]:
    m = inv["meta"]
    lines = [f"[ok] {m['name'] or '(unnamed)'} {m['version'] or ''} files={m['files']} code_lines={m['code_lines']} commit={m['commit'] or '-'}"]
    for stack in ("python", "ts"):
        c = inv["code"][stack]
        if c:
            lines.append(f"[ok] {stack}: units={len(c['units'])} edges={len(c['import_graph'])} layers={len(c['layers']['layers'])} cycles={len(c['layers']['cycles'])} contracts={len(c['contracts'])}")
    lines.append(f"[ok] storage={len(inv['storage'])} external={len(inv['external'])} env={len(inv['env'])} urls={len(inv['urls'])} mcp={len(inv['mcp'])}")
    lines.append(f"[ok] entrypoints={len(inv['entrypoints'])} workflows={len(inv['infra']['workflows'])} dockerfiles={len(inv['infra']['dockerfiles'])}")
    if m["capped"]:
        lines.append(f"[!] capped at {m['files']} files")
    if len(m["roots"]) > 1:
        lines.append(f"[!] {len(m['roots'])} roots found: {', '.join(m['roots'])} -> ask which one to map")
    if inv["unresolved"]:
        lines.append(f"[!] unresolved={len(inv['unresolved'])}")
    lines.append(f"[ok] done in {inv['duration_s']}s")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inventory a repository into JSON (stdlib only).")
    parser.add_argument("root")
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-files", type=int, default=MAX_FILES_DEFAULT)
    parser.add_argument("--diff", help="path to a previous inventory.json to compare against")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"[x] not a directory: {root}")
        return 2
    if args.max_files < 1:
        print("[x] --max-files must be >= 1")
        return 2
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    inv = build(root, args.max_files, exclude=out.resolve())
    if args.diff:
        previous = Path(args.diff)
        if previous.is_file():
            # A previous file that cannot be read is a lost comparison, not a lost run.
            try:
                old = json.loads(previous.read_text(encoding="utf-8"))
                if not isinstance(old, dict):
                    raise ValueError(f"not an inventory object: {type(old).__name__}")
                if old.get("schema") != SCHEMA_VERSION:
                    raise ValueError(f"schema {old.get('schema')!r}, expected {SCHEMA_VERSION}")
                rendered = render(diff(old, inv))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                print(f"[!] cannot diff against {previous}: {exc}")
            else:
                print("[diff] against " + str(previous))
                print(rendered)
        else:
            print(f"[diff] no previous inventory at {previous}")
    out.write_text(json.dumps(inv, indent=2, ensure_ascii=True), encoding="utf-8")
    for line in summary(inv):
        print(line)
    print(f"[ok] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
