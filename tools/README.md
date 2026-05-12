# tools/

Generic, schema-agnostic helpers shared across routines. Every function here
takes the routine's data and paths as parameters — nothing hardcodes a
specific payload shape, schema name, or webhook URL.

## Modules

### `assemble_payload.py`

```python
from tools.assemble_payload import assemble_final_payload

payload = assemble_final_payload(
    research_output=research,    # dict
    newsletter_output=newsletter,
    linkedin_output=linkedin,
    pipeline_version="1.0",      # optional
    dispatched_at=None,          # optional; auto UTC if None
)
```

Returns the assembled `final_payload` dict per `final_payload.schema.json`.
Pure function — no I/O, no env reads.

### `validate_payload.py`

```python
from tools.validate_payload import validate, ValidationError

validate(
    payload,
    schema_path="routines/<r>/pipeline/schemas/foo.schema.json",
    schemas_dir="routines/<r>/pipeline/schemas",   # optional, enables $ref
)
```

Raises `ValidationError` with all errors joined into the message. Use
`schemas_dir` when the schema references sibling schemas via `$ref`.

### `post_to_n8n.py`

```python
from tools.post_to_n8n import post_payload

result = post_payload(
    payload,
    webhook_url=os.environ["WEEKLY_AI_WEBHOOK_URL"],
    source_header="claude-code-routine",
    retries=1,
    archive_path=Path.home() / "ai-pipeline-archive" / f"{week_ref}.json",
)
# result = {"status": "ok"|"error", "http_code": int, "response": dict|str, "attempts": int}
```

Generic POST with retries, optional archiving. Schema-agnostic — caller
validates first.

## Adding a new tool

Helpers belong here only when they are:

1. **Generic** — usable by more than one routine without modification.
2. **Schema-agnostic** — never hardcode a payload field name.
3. **Pure-ish** — minimize hidden state; prefer explicit parameters over env reads.

Anything that knows the structure of a specific payload (e.g.
"compute newsletter read time from bullets") belongs in the routine, not
in `tools/`.
