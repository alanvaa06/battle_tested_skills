# Weekly AI Content — Coordinator

You are running the weekly AI content pipeline. Your job is to orchestrate
three skills in sequence, enforce the data contract between them, assemble
the final payload, dispatch it to n8n, and print a terminal report. You do
not produce content yourself — each skill does that.

## Required environment variables

- `WEEKLY_AI_WEBHOOK_URL` — full n8n webhook URL.
- `WEEKLY_AI_ARCHIVE_DIR` — optional; defaults to `~/ai-pipeline-archive`.
- `WEEKLY_AI_LANGUAGE` — optional; defaults to `English`.
- `WEEKLY_AI_REGION_FOCUS` — optional; defaults to `Global`.

If `WEEKLY_AI_WEBHOOK_URL` is not set, abort with an error before invoking
any skill.

## Step 1 — Run weekly-ai-research

Invoke the `weekly-ai-research` skill from
`routines/weekly-ai-content/skills/weekly-ai-research/` with:

- `pipeline_mode: true`
- `language: $WEEKLY_AI_LANGUAGE`
- `region_focus: $WEEKLY_AI_REGION_FOCUS`
- `research_window_days: 7`

The skill returns a `research_output` JSON object. Validate it:

```python
from tools.validate_payload import validate
validate(
    research_output,
    schema_path="routines/weekly-ai-content/pipeline/schemas/research_output.schema.json",
)
```

On failure: re-prompt the skill once with the specific failing check, then
abort if it fails again.

## Step 2a — Run email-newsletter-ai

Invoke the `email-newsletter-ai` skill with `pipeline_mode: true` and the
full `research_output` as input. Validate against
`pipeline/schemas/newsletter_output.schema.json`. Same retry rule.

## Step 2b — Run linkedin-alan-post

Invoke the `linkedin-alan-post` skill with `pipeline_mode: true` and the
full `research_output` as input. Validate against
`pipeline/schemas/linkedin_output.schema.json`. Same retry rule.

If the skill returns `pattern_used == "D"`, treat it as a validation
failure — Pattern D is banned in pipeline mode.

## Step 3 — Assemble the final payload

```python
from tools.assemble_payload import assemble_final_payload
final_payload = assemble_final_payload(
    research_output=research_output["research_output"],
    newsletter_output=newsletter_output["newsletter_output"],
    linkedin_output=linkedin_output["linkedin_output"],
)
```

Validate the result:

```python
validate(
    final_payload,
    schema_path="routines/weekly-ai-content/pipeline/schemas/final_payload.schema.json",
    schemas_dir="routines/weekly-ai-content/pipeline/schemas",
)
```

## Step 4 — Dispatch

```python
import os
from pathlib import Path
from tools.post_to_n8n import post_payload

archive_dir = Path(os.environ.get("WEEKLY_AI_ARCHIVE_DIR", str(Path.home() / "ai-pipeline-archive")))
result = post_payload(
    final_payload,
    webhook_url=os.environ["WEEKLY_AI_WEBHOOK_URL"],
    source_header="claude-code-routine",
    retries=1,
    archive_path=archive_dir / f"{final_payload['week_ref']}.json",
)
```

On `result["status"] == "error"`:
- Print the HTTP code and response body.
- Leave the archive in place (the payload survived).
- Exit non-zero.

## Step 5 — Terminal report

Print:

```
WEEKLY AI PIPELINE -- DISPATCHED
=================================
Week:               {final_payload['week_ref']}
Period:             {final_payload['week_start']} to {final_payload['week_end']}
Dispatched at:      {final_payload['dispatched_at']}
HTTP status:        {result['http_code']}
Attempts:           {result['attempts']}
Archived to:        {archive_dir / (final_payload['week_ref'] + '.json')}

RESEARCH
  Dominant theme:   {final_payload['research_summary']['dominant_theme']}
  Market mood:      {final_payload['research_summary']['market_mood']}
  Biggest move:     {final_payload['research_summary']['biggest_move_actor']}

NEWSLETTER
  Featured story:   {newsletter_output['newsletter_output']['section_1']['featured_story']['actor']}
  Bullet count:     {len(newsletter_output['newsletter_output']['section_2']['bullets'])}
  Read time:        {newsletter_output['newsletter_output']['meta']['estimated_read_time_seconds']}s

LINKEDIN
  Pattern:          {linkedin_output['linkedin_output']['meta']['pattern_used']}
  Hook:             {linkedin_output['linkedin_output']['post']['hook'][:80]}...
  Hashtags:         {' '.join(linkedin_output['linkedin_output']['post']['hashtags'])}
```

## Error handling reference

| Failure point | Action |
|---|---|
| Step 1 validation fails once | Re-prompt the research skill with the failing field |
| Step 1 validation fails twice | Abort; save error to `$WEEKLY_AI_ARCHIVE_DIR/<week_ref>-research-error.json` |
| Step 2a or 2b validation fails once | Re-prompt that skill |
| Step 2a or 2b validation fails twice | Abort; save error log |
| Step 4 POST returns non-2xx | retries=1 handles it; if still fails, archive + exit non-zero |
| n8n response body indicates error | Surface message, archive remains in place |

Never retry more than once at any failure point. Fail loudly and preserve
the payload so it can be manually re-dispatched.
