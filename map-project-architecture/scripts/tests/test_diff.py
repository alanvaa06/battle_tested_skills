"""diff: what changed between two inventories, rendered as ASCII."""
from __future__ import annotations

from diff import diff, render


def _inv(units, storage, external, entries):
    return {
        "code": {"python": {"units": [{"name": u} for u in units]}, "ts": None},
        "storage": [{"detector": s} for s in storage],
        "external": [{"detector": e} for e in external],
        "entrypoints": [{"kind": k, "name": n} for k, n in entries],
    }


def test_diff_lists_added_and_removed() -> None:
    old = _inv(["a", "b"], ["sqlalchemy"], [], [("project.scripts", "demo")])
    new = _inv(["a", "c"], [], ["requests"], [("project.scripts", "demo"), ("http_route", "api.py")])
    d = diff(old, new)
    assert d == {
        "units_added": ["c"], "units_removed": ["b"],
        "storage_added": [], "storage_removed": ["sqlalchemy"],
        "external_added": ["requests"], "external_removed": [],
        "entrypoints_added": ["http_route:api.py"], "entrypoints_removed": [],
    }
    text = render(d)
    assert "[+] unit c" in text and "[-] unit b" in text and "[-] storage sqlalchemy" in text


def test_no_changes() -> None:
    inv = _inv(["a"], [], [], [])
    assert render(diff(inv, inv)) == "[=] no changes since last inventory"
