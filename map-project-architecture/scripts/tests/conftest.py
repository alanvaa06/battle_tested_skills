"""Shared paths for the script tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make `scripts/` importable no matter which directory pytest was started from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FIXTURES = Path(__file__).parent / "fixtures"

# Fixture repos are scan targets, not test suites: never collect what is inside them.
collect_ignore_glob = ["fixtures/*"]


@pytest.fixture
def py_repo() -> Path:
    return FIXTURES / "py_repo"


@pytest.fixture
def ts_repo() -> Path:
    return FIXTURES / "ts_repo"
