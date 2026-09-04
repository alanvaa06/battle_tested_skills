"""graph: layer units by import direction and report cycles."""
from __future__ import annotations

from graph import layers


def _edges(pairs):
    return [{"from": a, "to": b, "count": 1} for a, b in pairs]


def test_layers_bottom_up() -> None:
    result = layers(["api", "cli", "core", "db"], _edges([("db", "core"), ("cli", "api"), ("cli", "db")]))
    assert result["layers"] == [["api", "core"], ["db"], ["cli"]]
    assert result["cycles"] == []


def test_cycle_is_reported_and_layered_together() -> None:
    result = layers(["a", "b", "c"], _edges([("a", "b"), ("b", "a"), ("c", "a")]))
    assert result["cycles"] == [["a", "b"]]
    assert result["layers"] == [["a", "b"], ["c"]]


def test_four_cycle_is_one_scc_in_one_layer() -> None:
    result = layers(["a", "b", "c", "d"], _edges([("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")]))
    assert result["cycles"] == [["a", "b", "c", "d"]]
    assert result["layers"] == [["a", "b", "c", "d"]]


def test_isolated_units_land_in_layer_zero() -> None:
    result = layers(["x", "y"], [])
    assert result["layers"] == [["x", "y"]]
    assert result["cycles"] == []
    assert "independent_pairs" not in result


def test_a_long_chain_does_not_recurse() -> None:
    units = [f"u{i}" for i in range(2000)]
    edges = [{"from": f"u{i}", "to": f"u{i + 1}", "count": 1} for i in range(1999)]
    result = layers(units, edges)
    assert len(result["layers"]) == 2000
    assert result["layers"][0] == ["u1999"]
    assert result["cycles"] == []
