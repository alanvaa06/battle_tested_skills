"""Layer a package graph by import direction (Tarjan SCC + longest path).

Both walks are iterative: a deep repository is a chain, not a tree, so a
recursive Tarjan or a recursive level function hits Python's recursion limit
on a few thousand units.
"""
from __future__ import annotations

from collections import defaultdict


def _tarjan(deps: dict[str, set[str]]) -> list[list[str]]:
    """Strongly connected components, in reverse topological order."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    sccs: list[list[str]] = []
    counter = 0

    for root in sorted(deps):
        if root in index:
            continue
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack.add(root)
        work: list[tuple[str, object]] = [(root, iter(sorted(deps[root])))]
        while work:
            v, it = work[-1]
            descended = False
            for w in it:  # type: ignore[union-attr]
                if w not in index:
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    on_stack.add(w)
                    work.append((w, iter(sorted(deps.get(w, set())))))
                    descended = True
                    break
                if w in on_stack:
                    low[v] = min(low[v], index[w])
            if descended:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[v])
            if low[v] == index[v]:
                comp: list[str] = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                sccs.append(sorted(comp))
    return sccs


def _levels(cdeps: dict[int, set[int]]) -> dict[int, int]:
    """Longest path to a sink, per component. cdeps is a DAG, so no cycle guard."""
    level: dict[int, int] = {}
    for start in cdeps:
        if start in level:
            continue
        stack = [start]
        while stack:
            i = stack[-1]
            if i in level:
                stack.pop()
                continue
            pending = [j for j in cdeps[i] if j not in level]
            if pending:
                stack.extend(pending)
                continue
            level[i] = 1 + max((level[j] for j in cdeps[i]), default=-1)
            stack.pop()
    return level


def layers(units: list[str], edges: list[dict]) -> dict:
    deps: dict[str, set[str]] = {u: set() for u in units}
    for e in edges:
        if e["from"] in deps and e["to"] in deps:
            deps[e["from"]].add(e["to"])
    sccs = _tarjan(deps)
    comp = {u: i for i, c in enumerate(sccs) for u in c}
    cdeps: dict[int, set[int]] = {i: set() for i in range(len(sccs))}
    for u, ds in deps.items():
        for d in ds:
            if comp[u] != comp[d]:
                cdeps[comp[u]].add(comp[d])
    level = _levels(cdeps)
    buckets: dict[int, list[str]] = defaultdict(list)
    for u in units:
        buckets[level[comp[u]]].append(u)
    depth = max(buckets, default=-1) + 1
    return {
        "layers": [sorted(buckets[k]) for k in range(depth)],
        "cycles": [c for c in sccs if len(c) > 1],
    }
