"""Generic final_payload assembler for the weekly AI pipeline.

Takes three sub-payloads (research, newsletter, linkedin) plus optional
pipeline_version and returns the assembled final_payload dict per
final_payload.schema.json. Pure function — no I/O.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def assemble_final_payload(
    *,
    research_output: dict[str, Any],
    newsletter_output: dict[str, Any],
    linkedin_output: dict[str, Any],
    pipeline_version: str = "1.0",
    dispatched_at: str | None = None,
) -> dict[str, Any]:
    """Combine the three sub-payloads into a final_payload dict.

    Args:
        research_output: research_output JSON body (without the outer wrapper).
        newsletter_output: newsletter_output JSON body (without the outer wrapper).
        linkedin_output: linkedin_output JSON body (without the outer wrapper).
        pipeline_version: semver-ish string (default "1.0").
        dispatched_at: ISO 8601 UTC timestamp; if None, fills with current UTC.

    Returns:
        A dict matching final_payload.schema.json.
    """
    if dispatched_at is None:
        dispatched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    r_meta = research_output["meta"]
    r_narr = research_output["narrative"]

    return {
        "pipeline_version": pipeline_version,
        "dispatched_at": dispatched_at,
        "week_ref": r_meta["week_ref"],
        "week_start": r_meta["week_start"],
        "week_end": r_meta["week_end"],
        "language": r_meta["language"],
        "research_summary": {
            "dominant_theme": r_narr["dominant_theme"],
            "market_mood": r_narr["market_mood"],
            "biggest_move_actor": r_narr["biggest_move"]["actor"],
            "items_evaluated": r_meta.get("items_evaluated", 0),
        },
        "newsletter": {
            "meta": newsletter_output["meta"],
            "section_1": newsletter_output["section_1"],
            "section_2": newsletter_output["section_2"],
            "editorial_notes": newsletter_output["editorial_notes"],
        },
        "linkedin": {
            "meta": linkedin_output["meta"],
            "post": linkedin_output["post"],
            "editorial_notes": linkedin_output["editorial_notes"],
        },
    }
