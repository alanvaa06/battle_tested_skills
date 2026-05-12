"""Test the generic tools.validate_payload helper."""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.validate_payload import validate, ValidationError

ROUTINE = REPO_ROOT / "routines" / "weekly-ai-content"
SCHEMAS = ROUTINE / "pipeline" / "schemas"
SYNTHETIC = ROUTINE / "pipeline" / "fixtures" / "synthetic"


def test_validate_research_fixture_passes():
    payload = json.loads((SYNTHETIC / "research_output.example.json").read_text(encoding="utf-8"))
    validate(payload, schema_path=SCHEMAS / "research_output.schema.json")


def test_validate_newsletter_fixture_passes():
    payload = json.loads((SYNTHETIC / "newsletter_output.example.json").read_text(encoding="utf-8"))
    validate(payload, schema_path=SCHEMAS / "newsletter_output.schema.json")


def test_validate_linkedin_fixture_passes():
    payload = json.loads((SYNTHETIC / "linkedin_output.example.json").read_text(encoding="utf-8"))
    validate(payload, schema_path=SCHEMAS / "linkedin_output.schema.json")


def test_validate_final_payload_resolves_refs():
    payload = json.loads((SYNTHETIC / "final_payload.example.json").read_text(encoding="utf-8"))
    validate(
        payload,
        schema_path=SCHEMAS / "final_payload.schema.json",
        schemas_dir=SCHEMAS,
    )


def test_validate_raises_on_bad_payload():
    with pytest.raises(ValidationError):
        validate({"obviously": "wrong"}, schema_path=SCHEMAS / "research_output.schema.json")
