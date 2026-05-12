"""Coordinator-style assembly: research + newsletter + linkedin -> final_payload.

Mirrors Step 3 of weekly-ai-coordinator-prompt.md. Validates against schema.
"""
import json
import pathlib
from datetime import datetime, timezone

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"

research = json.loads((FIX / "research_output.example.json").read_text(encoding="utf-8"))["research_output"]
newsletter = json.loads((FIX / "newsletter_output.example.json").read_text(encoding="utf-8"))["newsletter_output"]
linkedin = json.loads((FIX / "linkedin_output.example.json").read_text(encoding="utf-8"))["linkedin_output"]

final_payload = {
    "pipeline_version": "1.0",
    "dispatched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "week_ref": research["meta"]["week_ref"],
    "week_start": research["meta"]["week_start"],
    "week_end": research["meta"]["week_end"],
    "language": research["meta"]["language"],
    "research_summary": {
        "dominant_theme": research["narrative"]["dominant_theme"],
        "market_mood": research["narrative"]["market_mood"],
        "biggest_move_actor": research["narrative"]["biggest_move"]["actor"],
        "items_evaluated": research["meta"].get("items_evaluated", 0),
    },
    "newsletter": {
        "meta": newsletter["meta"],
        "section_1": newsletter["section_1"],
        "section_2": newsletter["section_2"],
        "editorial_notes": newsletter["editorial_notes"],
    },
    "linkedin": {
        "meta": linkedin["meta"],
        "post": linkedin["post"],
        "editorial_notes": linkedin["editorial_notes"],
    },
}

out_path = FIX / "final_payload.example.json"
out_path.write_text(json.dumps(final_payload, indent=2, ensure_ascii=False), encoding="utf-8")

# Validate against schema (with $ref resolution to sibling schemas)
schema_path = ROOT / "final_payload.schema.json"
schema = json.loads(schema_path.read_text(encoding="utf-8"))

# Build a resolver/registry so $refs to sibling files work
from referencing import Registry, Resource

resources = []
for name in ["final_payload", "newsletter_output", "linkedin_output", "research_output"]:
    s = json.loads((ROOT / f"{name}.schema.json").read_text(encoding="utf-8"))
    # Register under bare filename so $refs like "newsletter_output.schema.json#/..." resolve
    resources.append((f"{name}.schema.json", Resource.from_contents(s)))

registry = Registry().with_resources(resources)

validator = jsonschema.Draft202012Validator(schema, registry=registry)
errors = list(validator.iter_errors(final_payload))
if errors:
    for e in errors:
        print(f"INVALID at {list(e.absolute_path)}: {e.message}")
    raise SystemExit(1)
print(f"final_payload.example.json wrote {out_path.stat().st_size} bytes -- VALID")
