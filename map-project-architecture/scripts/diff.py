"""Compare two inventories and render the difference in ASCII."""
from __future__ import annotations


def _units(inv: dict) -> set[str]:
    names: set[str] = set()
    for stack in ("python", "ts"):
        c = (inv.get("code") or {}).get(stack)
        if c:
            names.update(u["name"] for u in c["units"])
    return names


def _names(items: list[dict], key: str) -> set[str]:
    return {i[key] for i in items}


def diff(old: dict, new: dict) -> dict:
    ou, nu = _units(old), _units(new)
    os_, ns = _names(old["storage"], "detector"), _names(new["storage"], "detector")
    oe, ne = _names(old["external"], "detector"), _names(new["external"], "detector")
    op = {f"{e['kind']}:{e['name']}" for e in old["entrypoints"]}
    np_ = {f"{e['kind']}:{e['name']}" for e in new["entrypoints"]}
    return {
        "units_added": sorted(nu - ou), "units_removed": sorted(ou - nu),
        "storage_added": sorted(ns - os_), "storage_removed": sorted(os_ - ns),
        "external_added": sorted(ne - oe), "external_removed": sorted(oe - ne),
        "entrypoints_added": sorted(np_ - op), "entrypoints_removed": sorted(op - np_),
    }


def render(d: dict) -> str:
    lines: list[str] = []
    for key, label in (("units", "unit"), ("storage", "storage"), ("external", "external"), ("entrypoints", "entrypoint")):
        lines.extend(f"[+] {label} {x}" for x in d[f"{key}_added"])
        lines.extend(f"[-] {label} {x}" for x in d[f"{key}_removed"])
    return "\n".join(lines) if lines else "[=] no changes since last inventory"
