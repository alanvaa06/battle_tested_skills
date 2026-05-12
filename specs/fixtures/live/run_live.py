"""Live end-to-end smoke test using real research from week 2026-W19.

Loads research_output, newsletter_output, linkedin_output from this dir;
validates each against its schema; assembles final_payload; validates that
too; writes final_payload.json; prints a terminal report.
"""
import json
import pathlib
from datetime import datetime, timezone

import jsonschema
from referencing import Registry, Resource

ROOT = pathlib.Path(__file__).resolve().parents[3]      # repo root
SCHEMA = ROOT / "specs"
LIVE = ROOT / "specs" / "fixtures" / "live"

def load_schema(name: str) -> dict:
    return json.loads((SCHEMA / f"{name}.schema.json").read_text(encoding="utf-8"))

def load_live(name: str) -> dict:
    return json.loads((LIVE / f"{name}.json").read_text(encoding="utf-8"))

resources = [
    (f"{n}.schema.json", Resource.from_contents(load_schema(n)))
    for n in ["final_payload", "newsletter_output", "linkedin_output", "research_output"]
]
registry = Registry().with_resources(resources)

def banner(s: str) -> None:
    print(f"\n{'=' * 70}\n{s}\n{'=' * 70}")

banner("STEP 1 -- weekly-ai-research output (LIVE data, week 2026-W19)")
research = load_live("research_output")
jsonschema.validate(research, load_schema("research_output"))
r = research["research_output"]
print(f"  [ok] research_output.schema.json")
print(f"  week_ref:        {r['meta']['week_ref']} ({r['meta']['week_start']} to {r['meta']['week_end']})")
print(f"  market_mood:     {r['narrative']['market_mood']}")
print(f"  biggest_move:    {r['narrative']['biggest_move']['actor']}")
print(f"  takeaways:       {len(r['narrative']['strategic_takeaways'])}")
print(f"  to_watch:        {len(r['narrative']['to_watch'])}")
print(f"  repos tracked:   {len(r['sections']['trending_repos']['repos'])}")
print(f"  items_evaluated: {r['meta']['items_evaluated']}")

banner("STEP 2a -- email-newsletter-ai output (LIVE)")
newsletter = load_live("newsletter_output")
jsonschema.validate(newsletter, load_schema("newsletter_output"))
nw = newsletter["newsletter_output"]
body_words = len(nw["section_1"]["featured_story"]["body"].split())
print(f"  [ok] newsletter_output.schema.json")
print(f"  body word count: {body_words} (must be 80-120)")
print(f"  bullet count:    {len(nw['section_2']['bullets'])} (must be 12-20)")
labels = {}
for b in nw["section_2"]["bullets"]:
    labels[b["label"]] = labels.get(b["label"], 0) + 1
print(f"  label mix:       {labels}")
print(f"  read time:       {nw['meta']['estimated_read_time_seconds']}s")

banner("STEP 2b -- linkedin-alan-post output (LIVE)")
linkedin = load_live("linkedin_output")
jsonschema.validate(linkedin, load_schema("linkedin_output"))
li = linkedin["linkedin_output"]
body = li["post"]["body"]
print(f"  [ok] linkedin_output.schema.json")
print(f"  pattern:         {li['meta']['pattern_used']}")
print(f"  hook_type:       {li['editorial_notes']['hook_type']}")
print(f"  word_count:      {len(body.split())}")
print(f"  char_count:      {len(body)}")
print(f"  hashtags:        {len(li['post']['hashtags'])}")
print(f"  limitations:     {li['editorial_notes']['limitations_included']}")
print(f"  alpha->beta:     {li['editorial_notes']['ai_alpha_beta_thesis_present']}")
print(f"  ready_to_paste:  {li['post']['ready_to_paste']}")

banner("STEP 3 -- assemble final_payload (LIVE)")
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
validator = jsonschema.Draft202012Validator(load_schema("final_payload"), registry=registry)
errors = list(validator.iter_errors(final_payload))
if errors:
    for e in errors:
        print(f"  FAIL at {list(e.absolute_path)}: {e.message}")
    raise SystemExit(1)
print(f"  [ok] final_payload.schema.json")

out = LIVE / "final_payload.json"
out.write_text(json.dumps(final_payload, indent=2, ensure_ascii=False), encoding="utf-8")
payload_bytes = out.stat().st_size
print(f"  written:         {out.relative_to(ROOT)} ({payload_bytes:,} bytes)")

banner("STEP 4 -- dispatch (DRY RUN -- no POST executed)")
print(f"  curl -X POST 'https://n8n.alanvaa.cloud/webhook/provex-ai-news-weekly' \\")
print(f"    -H 'Content-Type: application/json' \\")
print(f"    -H 'X-Source: claude-code-routine' \\")
print(f"    --data @{out.as_posix()} \\")
print(f"    --fail --max-time 60")

banner("STEP 6 -- TERMINAL REPORT (LIVE)")
print(f"  WEEKLY AI PIPELINE -- LIVE DRY RUN OK")
print(f"  =====================================")
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
print(f"    Word count:       {len(body.split())}")
print(f"    Hashtag count:    {len(li['post']['hashtags'])}")
print(f"")
print(f"  CHAIN INTEGRITY:    all 4 schemas validated on LIVE data.")
