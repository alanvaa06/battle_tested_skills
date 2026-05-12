"""End-to-end smoke test of the weekly AI pipeline.

Steps:
  1. Load research_output fixture (would come from weekly-ai-research skill).
  2. Validate it against schema (Step 1 validation gate in coordinator).
  3. Load newsletter_output fixture (would come from email-newsletter-ai skill).
  4. Validate (Step 2a gate).
  5. Load linkedin_output fixture (would come from linkedin-alan-post skill).
  6. Validate (Step 2b gate).
  7. Assemble final_payload (Step 3).
  8. Validate final_payload (pre-dispatch checklist).
  9. Simulate dispatch -- print curl command instead of POSTing.
 10. Print terminal report (Step 6).
"""
import json
import pathlib
from datetime import datetime, timezone

import jsonschema
from referencing import Registry, Resource

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"

WEBHOOK_URL = "https://n8n.alanvaa.cloud/webhook/provex-ai-news-weekly"

def load_schema(name: str) -> dict:
    return json.loads((ROOT / f"{name}.schema.json").read_text(encoding="utf-8"))

def load_fixture(name: str) -> dict:
    return json.loads((FIX / f"{name}.example.json").read_text(encoding="utf-8"))

def validate(name: str, payload: dict, registry: Registry | None = None) -> None:
    schema = load_schema(name)
    if registry is None:
        jsonschema.validate(payload, schema)
    else:
        validator = jsonschema.Draft202012Validator(schema, registry=registry)
        errors = list(validator.iter_errors(payload))
        if errors:
            for e in errors:
                print(f"  FAIL at {list(e.absolute_path)}: {e.message}")
            raise SystemExit(f"{name} validation failed")
    print(f"  [ok] {name}.schema.json")

def banner(s: str) -> None:
    print(f"\n{'=' * 70}\n{s}\n{'=' * 70}")

# Registry for cross-file $ref resolution in final_payload schema
resources = [
    (f"{n}.schema.json", Resource.from_contents(load_schema(n)))
    for n in ["final_payload", "newsletter_output", "linkedin_output", "research_output"]
]
registry = Registry().with_resources(resources)

banner("STEP 1 -- weekly-ai-research skill output")
research = load_fixture("research_output")
validate("research_output", research)
print(f"  week_ref:        {research['research_output']['meta']['week_ref']}")
print(f"  dominant_theme:  {research['research_output']['narrative']['dominant_theme']}")
print(f"  biggest_move:    {research['research_output']['narrative']['biggest_move']['actor']} -- {research['research_output']['narrative']['biggest_move']['move'][:80]}...")
print(f"  to_watch items:  {len(research['research_output']['narrative']['to_watch'])}")
print(f"  repos tracked:   {len(research['research_output']['sections']['trending_repos']['repos'])}")

banner("STEP 2a -- email-newsletter-ai skill output (consumes research_output)")
newsletter = load_fixture("newsletter_output")
validate("newsletter_output", newsletter)
nw = newsletter["newsletter_output"]
print(f"  intro preview:   {nw['section_1']['intro'][:100]}...")
print(f"  featured story:  {nw['section_1']['featured_story']['headline']}")
print(f"  body word count: {len(nw['section_1']['featured_story']['body'].split())} words")
print(f"  bullet count:    {len(nw['section_2']['bullets'])}")
labels = {}
for b in nw["section_2"]["bullets"]:
    labels[b["label"]] = labels.get(b["label"], 0) + 1
print(f"  label mix:       {labels}")

banner("STEP 2b -- linkedin-alan-post skill output (consumes research_output)")
linkedin = load_fixture("linkedin_output")
validate("linkedin_output", linkedin)
li = linkedin["linkedin_output"]
print(f"  pattern:         {li['meta']['pattern_used']}")
print(f"  hook type:       {li['editorial_notes']['hook_type']}")
print(f"  word count:      {li['meta']['word_count']}")
print(f"  hashtags:        {' '.join(li['post']['hashtags'])}")
print(f"  alpha->beta:     {li['editorial_notes']['ai_alpha_beta_thesis_present']}")
print(f"  limitations:     {li['editorial_notes']['limitations_included']}")
print(f"  ready_to_paste:  {li['post']['ready_to_paste']}")

banner("STEP 3 -- assemble final_payload")
r = research["research_output"]
final_payload = {
    "pipeline_version": "1.0",
    "dispatched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "week_ref": r["meta"]["week_ref"],
    "week_start": r["meta"]["week_start"],
    "week_end": r["meta"]["week_end"],
    "language": r["meta"]["language"],
    "research_summary": {
        "dominant_theme": r["narrative"]["dominant_theme"],
        "market_mood": r["narrative"]["market_mood"],
        "biggest_move_actor": r["narrative"]["biggest_move"]["actor"],
        "items_evaluated": r["meta"].get("items_evaluated", 0),
    },
    "newsletter": {
        "meta": nw["meta"],
        "section_1": nw["section_1"],
        "section_2": nw["section_2"],
        "editorial_notes": nw["editorial_notes"],
    },
    "linkedin": {
        "meta": li["meta"],
        "post": li["post"],
        "editorial_notes": li["editorial_notes"],
    },
}
validate("final_payload", final_payload, registry=registry)
payload_bytes = len(json.dumps(final_payload, ensure_ascii=False).encode("utf-8"))
print(f"  payload size:    {payload_bytes:,} bytes (limit: 5,242,880)")

banner("STEP 4 -- dispatch (DRY RUN -- no POST executed)")
print(f"  curl -X POST '{WEBHOOK_URL}' \\")
print(f"    -H 'Content-Type: application/json' \\")
print(f"    -H 'X-Source: claude-code-routine' \\")
print(f"    --data @/tmp/ai-pipeline-payload.json \\")
print(f"    --fail --max-time 60")

banner("STEP 6 -- TERMINAL REPORT")
print(f"  WEEKLY AI PIPELINE -- DRY RUN OK")
print(f"  =================================")
print(f"  Week:               {final_payload['week_ref']}")
print(f"  Period:             {final_payload['week_start']} to {final_payload['week_end']}")
print(f"  Dispatched at:      {final_payload['dispatched_at']}")
print(f"  Payload size:       {payload_bytes:,} bytes")
print(f"")
print(f"  RESEARCH")
print(f"    Dominant theme:   {final_payload['research_summary']['dominant_theme']}")
print(f"    Market mood:      {final_payload['research_summary']['market_mood']}")
print(f"    Biggest move:     {final_payload['research_summary']['biggest_move_actor']}")
print(f"")
print(f"  NEWSLETTER")
print(f"    Featured story:   {nw['section_1']['featured_story']['actor']}")
print(f"    Bullet count:     {len(nw['section_2']['bullets'])}")
print(f"    Read time:        {nw['meta']['estimated_read_time_seconds']}s")
print(f"")
print(f"  LINKEDIN")
print(f"    Pattern:          {li['meta']['pattern_used']}")
print(f"    Hook:             {li['post']['hook'][:80]}...")
print(f"    Word count:       {li['meta']['word_count']}")
print(f"    Hashtags:         {' '.join(li['post']['hashtags'])}")
print(f"")
print(f"  CHAIN INTEGRITY:    all 4 schemas validated, payload assembled cleanly.")
