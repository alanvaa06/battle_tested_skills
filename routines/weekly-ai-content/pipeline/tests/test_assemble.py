"""Test the generalized tools.assemble_payload function."""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.assemble_payload import assemble_final_payload


def test_assemble_from_dicts():
    research = {
        "meta": {
            "week_ref": "2026-W19",
            "week_start": "2026-05-04",
            "week_end": "2026-05-10",
            "language": "English",
            "items_evaluated": 12,
        },
        "narrative": {
            "dominant_theme": "compute is the constraint",
            "market_mood": "bullish",
            "biggest_move": {"actor": "Anthropic"},
        },
    }
    newsletter = {
        "meta": {"week_ref": "2026-W19"},
        "section_1": {},
        "section_2": {"bullets": []},
        "editorial_notes": {},
    }
    linkedin = {
        "meta": {"week_ref": "2026-W19"},
        "post": {"body": "test", "hashtags": ["#x", "#y", "#z"]},
        "editorial_notes": {},
    }

    payload = assemble_final_payload(
        research_output=research,
        newsletter_output=newsletter,
        linkedin_output=linkedin,
    )

    assert payload["pipeline_version"] == "1.0"
    assert payload["week_ref"] == "2026-W19"
    assert payload["week_start"] == "2026-05-04"
    assert payload["week_end"] == "2026-05-10"
    assert payload["language"] == "English"
    assert payload["research_summary"]["dominant_theme"] == "compute is the constraint"
    assert payload["research_summary"]["market_mood"] == "bullish"
    assert payload["research_summary"]["biggest_move_actor"] == "Anthropic"
    assert payload["research_summary"]["items_evaluated"] == 12
    assert "dispatched_at" in payload
    assert payload["newsletter"]["meta"]["week_ref"] == "2026-W19"
    assert payload["linkedin"]["post"]["body"] == "test"
