# Repo Layout for Claude Code Routines — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate `battle_tested_skills` from a flat skills+specs layout into a multi-routine repo (`routines/*`, `tools/*`, `docs/*`) without breaking the existing live pipeline or the `~/.claude/skills/` junctions.

**Architecture:** Each routine becomes a self-contained subtree under `routines/<name>/` with its own `skills/`, optional `pipeline/` (schemas + fixtures + tests), and a `coordinator.md` entry point. Shared generic plumbing (HTTP POST, schema validation, payload assembly) lives in `tools/` at the repo root and is parameterized — never hardcoding routine-specific field names. Migration moves files with `git mv` to preserve history, fixes path references in a separate commit, adds new helpers and coordinators, then re-points Windows junctions.

**Tech Stack:** Python 3.13+, `jsonschema` 4.x, `referencing` (for cross-file `$ref`), `requests`, Git, PowerShell (junctions).

**Spec:** `docs/2026-05-12-repo-layout-design.md`

---

## Pre-flight context (read once before starting)

Current repo state:

```
battle_tested_skills/                    # private GitHub repo
├── weekly-ai-research/SKILL.md          # junctioned from ~/.claude/skills/
├── linkedin-alan-post/SKILL.md          # junctioned
│   └── references/few_shot_examples.md
├── email-newsletter-ai/SKILL.md         # junctioned
├── specs/
│   ├── research_output.schema.json
│   ├── newsletter_output.schema.json
│   ├── linkedin_output.schema.json
│   ├── final_payload.schema.json
│   └── fixtures/
│       ├── research_output.example.json
│       ├── newsletter_output.example.json
│       ├── linkedin_output.example.json
│       ├── final_payload.example.json
│       ├── assemble_payload.py
│       ├── smoke_test.py
│       └── live/
│           ├── research_output.json
│           ├── newsletter_output.json
│           ├── linkedin_output.json
│           ├── final_payload.json
│           └── run_live.py
└── docs/
    └── 2026-05-12-repo-layout-design.md
```

Junctions (read-only references; do not edit through them):

```
~/.claude/skills/weekly-ai-research   →  battle_tested_skills/weekly-ai-research
~/.claude/skills/email-newsletter-ai  →  battle_tested_skills/email-newsletter-ai
~/.claude/skills/linkedin-alan-post   →  battle_tested_skills/linkedin-alan-post
```

`origin/main` head: `dbb36af` (docs spec). Local `main` is ahead by 2 commits (`dbb36af`, `3507758`) — these must be pushed before this plan starts OR pushed together at the end. Recommended: push them when the rest is ready, in one explicit batch.

---

## Task 1: Commit pending live fixtures

**Files:**
- Stage: `specs/fixtures/live/research_output.json`
- Stage: `specs/fixtures/live/newsletter_output.json`
- Stage: `specs/fixtures/live/linkedin_output.json`
- Stage: `specs/fixtures/live/final_payload.json`
- Stage: `specs/fixtures/live/run_live.py`

- [ ] **Step 1: Confirm files exist and have content**

Run:
```bash
ls -la specs/fixtures/live/
```
Expected: five files, all non-empty.

- [ ] **Step 2: Stage and commit**

```bash
git add specs/fixtures/live/research_output.json \
        specs/fixtures/live/newsletter_output.json \
        specs/fixtures/live/linkedin_output.json \
        specs/fixtures/live/final_payload.json \
        specs/fixtures/live/run_live.py
git commit -m "test: add live week-2026-W19 smoke test outputs"
```

- [ ] **Step 3: Verify clean tree**

Run:
```bash
git status --short
```
Expected: empty output.

---

## Task 2: Create the new directory skeleton

**Files:**
- Create: `routines/weekly-ai-content/`
- Create: `routines/weekly-ai-content/skills/`
- Create: `routines/weekly-ai-content/pipeline/schemas/`
- Create: `routines/weekly-ai-content/pipeline/fixtures/synthetic/`
- Create: `routines/weekly-ai-content/pipeline/fixtures/live/`
- Create: `routines/weekly-ai-content/pipeline/tests/`
- Create: `tools/`

- [ ] **Step 1: Create dirs**

Run:
```bash
mkdir -p routines/weekly-ai-content/skills
mkdir -p routines/weekly-ai-content/pipeline/schemas
mkdir -p routines/weekly-ai-content/pipeline/fixtures/synthetic
mkdir -p routines/weekly-ai-content/pipeline/fixtures/live
mkdir -p routines/weekly-ai-content/pipeline/tests
mkdir -p tools
```

- [ ] **Step 2: Verify**

Run:
```bash
find routines tools -type d | sort
```
Expected:
```
routines
routines/weekly-ai-content
routines/weekly-ai-content/pipeline
routines/weekly-ai-content/pipeline/fixtures
routines/weekly-ai-content/pipeline/fixtures/live
routines/weekly-ai-content/pipeline/fixtures/synthetic
routines/weekly-ai-content/pipeline/schemas
routines/weekly-ai-content/pipeline/tests
routines/weekly-ai-content/skills
tools
```

No commit yet — committed together with Task 3.

---

## Task 3: Move skills with git mv

**Files:**
- Move: `weekly-ai-research/` → `routines/weekly-ai-content/skills/weekly-ai-research/`
- Move: `email-newsletter-ai/` → `routines/weekly-ai-content/skills/email-newsletter-ai/`
- Move: `linkedin-alan-post/` → `routines/weekly-ai-content/skills/linkedin-alan-post/`

- [ ] **Step 1: Move all three skill folders**

Run:
```bash
git mv weekly-ai-research    routines/weekly-ai-content/skills/
git mv email-newsletter-ai   routines/weekly-ai-content/skills/
git mv linkedin-alan-post    routines/weekly-ai-content/skills/
```

- [ ] **Step 2: Verify SKILL.md files moved with history**

Run:
```bash
git log --follow --oneline -- routines/weekly-ai-content/skills/weekly-ai-research/SKILL.md | head -3
```
Expected: at least two commits visible (the initial commit and the pipeline_mode addition).

---

## Task 4: Move schemas with git mv

**Files:**
- Move: `specs/research_output.schema.json` → `routines/weekly-ai-content/pipeline/schemas/research_output.schema.json`
- Move: `specs/newsletter_output.schema.json` → `routines/weekly-ai-content/pipeline/schemas/newsletter_output.schema.json`
- Move: `specs/linkedin_output.schema.json` → `routines/weekly-ai-content/pipeline/schemas/linkedin_output.schema.json`
- Move: `specs/final_payload.schema.json` → `routines/weekly-ai-content/pipeline/schemas/final_payload.schema.json`

- [ ] **Step 1: Move the 4 schemas**

Run:
```bash
git mv specs/research_output.schema.json   routines/weekly-ai-content/pipeline/schemas/
git mv specs/newsletter_output.schema.json routines/weekly-ai-content/pipeline/schemas/
git mv specs/linkedin_output.schema.json   routines/weekly-ai-content/pipeline/schemas/
git mv specs/final_payload.schema.json     routines/weekly-ai-content/pipeline/schemas/
```

- [ ] **Step 2: Verify**

Run:
```bash
ls routines/weekly-ai-content/pipeline/schemas/
```
Expected:
```
final_payload.schema.json
linkedin_output.schema.json
newsletter_output.schema.json
research_output.schema.json
```

---

## Task 5: Move synthetic fixtures

**Files:**
- Move: `specs/fixtures/research_output.example.json` → `routines/weekly-ai-content/pipeline/fixtures/synthetic/research_output.example.json`
- Move: `specs/fixtures/newsletter_output.example.json` → `routines/weekly-ai-content/pipeline/fixtures/synthetic/newsletter_output.example.json`
- Move: `specs/fixtures/linkedin_output.example.json` → `routines/weekly-ai-content/pipeline/fixtures/synthetic/linkedin_output.example.json`
- Move: `specs/fixtures/final_payload.example.json` → `routines/weekly-ai-content/pipeline/fixtures/synthetic/final_payload.example.json`

- [ ] **Step 1: Move synthetic fixtures**

Run:
```bash
git mv specs/fixtures/research_output.example.json   routines/weekly-ai-content/pipeline/fixtures/synthetic/
git mv specs/fixtures/newsletter_output.example.json routines/weekly-ai-content/pipeline/fixtures/synthetic/
git mv specs/fixtures/linkedin_output.example.json   routines/weekly-ai-content/pipeline/fixtures/synthetic/
git mv specs/fixtures/final_payload.example.json     routines/weekly-ai-content/pipeline/fixtures/synthetic/
```

- [ ] **Step 2: Verify**

Run:
```bash
ls routines/weekly-ai-content/pipeline/fixtures/synthetic/
```
Expected: 4 `.example.json` files.

---

## Task 6: Move live fixtures + live run script

**Files:**
- Move: `specs/fixtures/live/research_output.json` → `routines/weekly-ai-content/pipeline/fixtures/live/research_output.json`
- Move: `specs/fixtures/live/newsletter_output.json` → `routines/weekly-ai-content/pipeline/fixtures/live/newsletter_output.json`
- Move: `specs/fixtures/live/linkedin_output.json` → `routines/weekly-ai-content/pipeline/fixtures/live/linkedin_output.json`
- Move: `specs/fixtures/live/final_payload.json` → `routines/weekly-ai-content/pipeline/fixtures/live/final_payload.json`
- Move: `specs/fixtures/live/run_live.py` → `routines/weekly-ai-content/pipeline/tests/run_live.py`

- [ ] **Step 1: Move live JSON outputs**

Run:
```bash
git mv specs/fixtures/live/research_output.json   routines/weekly-ai-content/pipeline/fixtures/live/
git mv specs/fixtures/live/newsletter_output.json routines/weekly-ai-content/pipeline/fixtures/live/
git mv specs/fixtures/live/linkedin_output.json   routines/weekly-ai-content/pipeline/fixtures/live/
git mv specs/fixtures/live/final_payload.json     routines/weekly-ai-content/pipeline/fixtures/live/
```

- [ ] **Step 2: Move run_live.py to tests/**

Run:
```bash
git mv specs/fixtures/live/run_live.py routines/weekly-ai-content/pipeline/tests/
```

- [ ] **Step 3: Verify**

Run:
```bash
ls routines/weekly-ai-content/pipeline/fixtures/live/
ls routines/weekly-ai-content/pipeline/tests/
```
Expected:
```
final_payload.json
linkedin_output.json
newsletter_output.json
research_output.json
---
run_live.py
```

---

## Task 7: Move smoke_test.py + assemble_payload.py

**Files:**
- Move: `specs/fixtures/smoke_test.py` → `routines/weekly-ai-content/pipeline/tests/smoke_test.py`
- Move: `specs/fixtures/assemble_payload.py` → `tools/assemble_payload.py`

- [ ] **Step 1: Move smoke test**

Run:
```bash
git mv specs/fixtures/smoke_test.py routines/weekly-ai-content/pipeline/tests/
```

- [ ] **Step 2: Move assemble_payload to tools/**

Run:
```bash
git mv specs/fixtures/assemble_payload.py tools/assemble_payload.py
```

- [ ] **Step 3: Remove empty specs/ tree**

Run:
```bash
rmdir specs/fixtures/live specs/fixtures specs
```
Expected: no errors. If `rmdir` fails on `specs/`, list contents — anything left needs to be moved or deleted.

- [ ] **Step 4: Verify specs/ is gone**

Run:
```bash
ls specs 2>&1 || echo "specs/ removed (expected)"
```
Expected: `specs/ removed (expected)` (or platform equivalent "No such file or directory").

---

## Task 8: Commit the move

- [ ] **Step 1: Inspect staged moves**

Run:
```bash
git status --short
```
Expected output lists exclusively `R` (renamed) entries — no `M` (modified), no `A` (added). If any file is modified, abort and fix before committing — modifying during `git mv` breaks rename detection.

- [ ] **Step 2: Commit**

```bash
git commit -m "refactor: move to routines/* + tools/* layout

Phase 1 of the layout migration described in
docs/2026-05-12-repo-layout-design.md. Moves only — no content
edits. Path fixes follow in the next commit.

- weekly-ai-research, email-newsletter-ai, linkedin-alan-post
  -> routines/weekly-ai-content/skills/
- specs/*.schema.json
  -> routines/weekly-ai-content/pipeline/schemas/
- specs/fixtures/*.example.json
  -> routines/weekly-ai-content/pipeline/fixtures/synthetic/
- specs/fixtures/live/*.json
  -> routines/weekly-ai-content/pipeline/fixtures/live/
- specs/fixtures/smoke_test.py, run_live.py
  -> routines/weekly-ai-content/pipeline/tests/
- specs/fixtures/assemble_payload.py
  -> tools/assemble_payload.py"
```

- [ ] **Step 3: Verify history preserved on a sample file**

Run:
```bash
git log --follow --oneline routines/weekly-ai-content/skills/linkedin-alan-post/SKILL.md | head -5
```
Expected: at least 3 commits (initial, pipeline_mode addition, the rename commit). If only the rename shows, history was lost — investigate before continuing.

---

## Task 9: Generalize tools/assemble_payload.py

**Files:**
- Modify: `tools/assemble_payload.py`

The current file hardcodes paths and writes to a fixed location. Convert it to a parameterized library function plus a thin CLI.

- [ ] **Step 1: Read the current contents**

Run:
```bash
cat tools/assemble_payload.py
```
Note: the file currently composes `final_payload` from three sibling fixtures and writes a hardcoded output path.

- [ ] **Step 2: Write a test for the new shape**

Create `routines/weekly-ai-content/pipeline/tests/test_assemble.py`:

```python
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
```

- [ ] **Step 3: Run the test and watch it fail**

Run:
```bash
python -m pytest routines/weekly-ai-content/pipeline/tests/test_assemble.py -v
```
Expected: `ImportError: cannot import name 'assemble_final_payload' from 'tools.assemble_payload'` OR similar failure.

- [ ] **Step 4: Rewrite tools/assemble_payload.py with the new shape**

Overwrite `tools/assemble_payload.py`:

```python
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
```

- [ ] **Step 5: Run the test and watch it pass**

Run:
```bash
python -m pytest routines/weekly-ai-content/pipeline/tests/test_assemble.py -v
```
Expected: PASS.

- [ ] **Step 6: Stage and verify**

Run:
```bash
git add tools/assemble_payload.py routines/weekly-ai-content/pipeline/tests/test_assemble.py
git status --short
```
Expected: M tools/assemble_payload.py, A routines/weekly-ai-content/pipeline/tests/test_assemble.py.

---

## Task 10: Create tools/__init__.py

**Files:**
- Create: `tools/__init__.py`

- [ ] **Step 1: Create the package marker**

```bash
echo '"""Generic plumbing shared across routines."""' > tools/__init__.py
```

- [ ] **Step 2: Confirm import works**

Run:
```bash
python -c "from tools import assemble_payload; print(assemble_payload.__name__)"
```
Expected: `tools.assemble_payload`.

- [ ] **Step 3: Stage**

Run:
```bash
git add tools/__init__.py
```

---

## Task 11: Build tools/validate_payload.py (TDD)

**Files:**
- Create: `routines/weekly-ai-content/pipeline/tests/test_validate.py`
- Create: `tools/validate_payload.py`

- [ ] **Step 1: Write the failing test**

Create `routines/weekly-ai-content/pipeline/tests/test_validate.py`:

```python
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
```

- [ ] **Step 2: Run it and watch it fail**

Run:
```bash
python -m pytest routines/weekly-ai-content/pipeline/tests/test_validate.py -v
```
Expected: ImportError on `tools.validate_payload`.

- [ ] **Step 3: Implement tools/validate_payload.py**

Create `tools/validate_payload.py`:

```python
"""Generic JSON Schema validator with cross-file $ref resolution.

Schema-agnostic — caller supplies the schema path. Works for any routine.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
from referencing import Registry, Resource


class ValidationError(ValueError):
    """Raised when a payload fails schema validation."""


def validate(
    payload: dict[str, Any],
    *,
    schema_path: str | Path,
    schemas_dir: str | Path | None = None,
) -> None:
    """Validate `payload` against the schema at `schema_path`.

    If `schemas_dir` is provided, every `*.schema.json` file in that
    directory is registered under its bare filename so cross-file `$ref`
    pointers resolve.

    Raises:
        ValidationError: if any validation error is detected, with all
            errors joined into the message.
    """
    schema_path = Path(schema_path)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    if schemas_dir is not None:
        resources = []
        for f in sorted(Path(schemas_dir).glob("*.schema.json")):
            resources.append((f.name, Resource.from_contents(
                json.loads(f.read_text(encoding="utf-8"))
            )))
        registry = Registry().with_resources(resources)
        validator = jsonschema.Draft202012Validator(schema, registry=registry)
    else:
        validator = jsonschema.Draft202012Validator(schema)

    errors = list(validator.iter_errors(payload))
    if errors:
        msgs = [f"{list(e.absolute_path)}: {e.message}" for e in errors]
        raise ValidationError("; ".join(msgs))
```

- [ ] **Step 4: Run the test and watch it pass**

Run:
```bash
python -m pytest routines/weekly-ai-content/pipeline/tests/test_validate.py -v
```
Expected: 5 tests pass.

- [ ] **Step 5: Stage**

Run:
```bash
git add tools/validate_payload.py routines/weekly-ai-content/pipeline/tests/test_validate.py
```

---

## Task 12: Build tools/post_to_n8n.py (TDD with mock)

**Files:**
- Create: `routines/weekly-ai-content/pipeline/tests/test_post.py`
- Create: `tools/post_to_n8n.py`

- [ ] **Step 1: Write the failing test**

Create `routines/weekly-ai-content/pipeline/tests/test_post.py`:

```python
"""Test the generic tools.post_to_n8n helper. No network — mocks only."""
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.post_to_n8n import post_payload


def _mock_response(status_code: int, body: dict | str):
    m = MagicMock()
    m.status_code = status_code
    if isinstance(body, dict):
        m.json.return_value = body
        m.text = json.dumps(body)
    else:
        m.json.side_effect = ValueError
        m.text = body
    return m


def test_post_success_returns_ok(tmp_path):
    archive = tmp_path / "archive" / "test.json"
    with patch("tools.post_to_n8n.requests.post") as p:
        p.return_value = _mock_response(200, {"id": "abc"})
        result = post_payload(
            {"hello": "world"},
            webhook_url="https://example/webhook",
            archive_path=archive,
        )
    assert result["status"] == "ok"
    assert result["http_code"] == 200
    assert result["attempts"] == 1
    assert result["response"] == {"id": "abc"}
    assert archive.exists()
    assert json.loads(archive.read_text())["hello"] == "world"


def test_post_retries_on_failure():
    with patch("tools.post_to_n8n.requests.post") as p, \
         patch("tools.post_to_n8n.time.sleep"):
        p.side_effect = [
            _mock_response(500, "server boom"),
            _mock_response(200, {"id": "ok"}),
        ]
        result = post_payload(
            {"x": 1},
            webhook_url="https://example/webhook",
            retries=1,
        )
    assert result["status"] == "ok"
    assert result["http_code"] == 200
    assert result["attempts"] == 2


def test_post_gives_up_after_retries():
    with patch("tools.post_to_n8n.requests.post") as p, \
         patch("tools.post_to_n8n.time.sleep"):
        p.return_value = _mock_response(500, "still bad")
        result = post_payload(
            {"x": 1},
            webhook_url="https://example/webhook",
            retries=2,
        )
    assert result["status"] == "error"
    assert result["attempts"] == 3
    assert "HTTP 500" in result["response"]


def test_post_sends_correct_headers():
    with patch("tools.post_to_n8n.requests.post") as p:
        p.return_value = _mock_response(200, {"ok": True})
        post_payload(
            {"x": 1},
            webhook_url="https://example/webhook",
            source_header="claude-code-routine",
        )
    call_kwargs = p.call_args.kwargs
    assert call_kwargs["headers"]["X-Source"] == "claude-code-routine"
    assert call_kwargs["headers"]["Content-Type"] == "application/json"
    assert call_kwargs["json"] == {"x": 1}
```

- [ ] **Step 2: Run and watch it fail**

Run:
```bash
python -m pytest routines/weekly-ai-content/pipeline/tests/test_post.py -v
```
Expected: ImportError on `tools.post_to_n8n`.

- [ ] **Step 3: Implement tools/post_to_n8n.py**

Create `tools/post_to_n8n.py`:

```python
"""Generic n8n webhook POST helper. Schema-agnostic.

The routine assembles + validates its own payload, then hands it here.
This module knows nothing about specific payload shapes.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests


def post_payload(
    payload: dict[str, Any],
    *,
    webhook_url: str,
    source_header: str = "claude-code-routine",
    timeout: int = 60,
    retries: int = 1,
    retry_sleep_seconds: int = 60,
    archive_path: Path | None = None,
) -> dict[str, Any]:
    """POST a JSON payload to an n8n webhook.

    Args:
        payload: dict to send (already assembled + schema-validated by caller).
        webhook_url: full URL of the n8n webhook.
        source_header: value for the X-Source header (default 'claude-code-routine').
        timeout: per-request timeout in seconds.
        retries: number of retries after the first failure.
        retry_sleep_seconds: pause between attempts.
        archive_path: if provided, the payload is written there before POSTing.

    Returns:
        {
            "status":   "ok" | "error",
            "http_code": int,
            "response":  dict | str,    # parsed JSON if possible, else text
            "attempts":  int,
        }
    """
    if archive_path is not None:
        archive_path = Path(archive_path)
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    attempt = 0
    last_err: str | None = None
    headers = {"X-Source": source_header, "Content-Type": "application/json"}

    while attempt <= retries:
        attempt += 1
        try:
            r = requests.post(webhook_url, json=payload, headers=headers, timeout=timeout)
            if 200 <= r.status_code < 300:
                try:
                    body: dict | str = r.json()
                except ValueError:
                    body = r.text
                return {
                    "status": "ok",
                    "http_code": r.status_code,
                    "response": body,
                    "attempts": attempt,
                }
            last_err = f"HTTP {r.status_code}: {r.text[:500]}"
        except requests.RequestException as e:
            last_err = str(e)

        if attempt <= retries:
            time.sleep(retry_sleep_seconds)

    return {
        "status": "error",
        "http_code": 0,
        "response": last_err or "unknown error",
        "attempts": attempt,
    }
```

- [ ] **Step 4: Run and watch it pass**

Run:
```bash
python -m pytest routines/weekly-ai-content/pipeline/tests/test_post.py -v
```
Expected: 4 tests pass.

- [ ] **Step 5: Stage**

Run:
```bash
git add tools/post_to_n8n.py routines/weekly-ai-content/pipeline/tests/test_post.py
```

---

## Task 13: Fix paths in the moved tests

**Files:**
- Modify: `routines/weekly-ai-content/pipeline/tests/smoke_test.py`
- Modify: `routines/weekly-ai-content/pipeline/tests/run_live.py`

Both files currently compute `ROOT` and walk `parents[N]` to find schemas; the new depth changes that.

- [ ] **Step 1: Open smoke_test.py and update ROOT**

In `routines/weekly-ai-content/pipeline/tests/smoke_test.py`, find:

```python
ROOT = pathlib.Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"
```

Replace with:

```python
ROOT = pathlib.Path(__file__).resolve().parents[2]     # routine root (weekly-ai-content)
SCHEMA = ROOT / "pipeline" / "schemas"
FIX = ROOT / "pipeline" / "fixtures" / "synthetic"
```

Then replace every `load_schema(name)` body to use `SCHEMA / f"{name}.schema.json"` and every `load_fixture(name)` body to use `FIX / f"{name}.example.json"`.

Final smoke_test.py header:

```python
"""End-to-end smoke test using synthetic fixtures.

Runs the four schema validations and final payload assembly. No network.
"""
import json
import pathlib
from datetime import datetime, timezone

import jsonschema
from referencing import Registry, Resource

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "pipeline" / "schemas"
FIX = ROOT / "pipeline" / "fixtures" / "synthetic"


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA / f"{name}.schema.json").read_text(encoding="utf-8"))


def load_fixture(name: str) -> dict:
    return json.loads((FIX / f"{name}.example.json").read_text(encoding="utf-8"))
```

Leave the rest of the smoke test body unchanged.

- [ ] **Step 2: Run smoke test and watch it pass**

Run:
```bash
python routines/weekly-ai-content/pipeline/tests/smoke_test.py
```
Expected: "CHAIN INTEGRITY: all 4 schemas validated, payload assembled cleanly." in the output.

- [ ] **Step 3: Open run_live.py and update ROOT**

In `routines/weekly-ai-content/pipeline/tests/run_live.py`, find:

```python
ROOT = pathlib.Path(__file__).resolve().parents[3]      # repo root
SCHEMA = ROOT / "specs"
LIVE = ROOT / "specs" / "fixtures" / "live"
```

Replace with:

```python
ROUTINE = pathlib.Path(__file__).resolve().parents[2]   # routine root
SCHEMA = ROUTINE / "pipeline" / "schemas"
LIVE = ROUTINE / "pipeline" / "fixtures" / "live"
```

Then update references in `load_schema` and `load_live` to use the new dirs.

Final run_live.py header:

```python
"""Live end-to-end smoke test using real research data.

Loads research_output, newsletter_output, linkedin_output from
pipeline/fixtures/live/; validates each against its schema; assembles
final_payload; validates that too; prints a terminal report.
"""
import json
import pathlib
from datetime import datetime, timezone

import jsonschema
from referencing import Registry, Resource

ROUTINE = pathlib.Path(__file__).resolve().parents[2]
SCHEMA = ROUTINE / "pipeline" / "schemas"
LIVE = ROUTINE / "pipeline" / "fixtures" / "live"


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA / f"{name}.schema.json").read_text(encoding="utf-8"))


def load_live(name: str) -> dict:
    return json.loads((LIVE / f"{name}.json").read_text(encoding="utf-8"))
```

Leave the rest of the run_live.py body unchanged (the rest already operates on `ROUTINE` / `LIVE` paths).

- [ ] **Step 4: Run live runner and watch it pass**

Run:
```bash
python routines/weekly-ai-content/pipeline/tests/run_live.py
```
Expected: "CHAIN INTEGRITY: all 4 schemas validated on LIVE data." in the output.

- [ ] **Step 5: Stage**

Run:
```bash
git add routines/weekly-ai-content/pipeline/tests/smoke_test.py \
        routines/weekly-ai-content/pipeline/tests/run_live.py
```

---

## Task 14: Audit SKILL.md files for stale path references

**Files:**
- Modify if needed: `routines/weekly-ai-content/skills/weekly-ai-research/SKILL.md`
- Modify if needed: `routines/weekly-ai-content/skills/email-newsletter-ai/SKILL.md`
- Modify if needed: `routines/weekly-ai-content/skills/linkedin-alan-post/SKILL.md`

- [ ] **Step 1: Grep all three SKILL.md files for old paths**

Run:
```bash
grep -nE "specs/(fixtures|.*schema\.json)" routines/weekly-ai-content/skills/*/SKILL.md
```

Expected outcomes:
- `weekly-ai-research/SKILL.md` references `specs/research_output.schema.json` and `specs/fixtures/research_output.example.json`.
- `linkedin-alan-post/SKILL.md` references `specs/research_output.schema.json`, `specs/linkedin_output.schema.json`, and `specs/fixtures/linkedin_output.example.json`.
- `email-newsletter-ai/SKILL.md` may or may not reference `specs/...` paths.

- [ ] **Step 2: Update references**

For each match, change:

```
specs/research_output.schema.json
```
to:
```
pipeline/schemas/research_output.schema.json
```

And:
```
specs/fixtures/research_output.example.json
```
to:
```
pipeline/fixtures/synthetic/research_output.example.json
```

(Apply the same pattern to all four output names.)

- [ ] **Step 3: Re-run the grep to confirm zero remaining hits**

Run:
```bash
grep -nE "specs/(fixtures|.*schema\.json)" routines/weekly-ai-content/skills/*/SKILL.md || echo "clean"
```
Expected: `clean`.

- [ ] **Step 4: Stage**

Run:
```bash
git add routines/weekly-ai-content/skills/
```

---

## Task 15: Commit the path/code fixes

- [ ] **Step 1: Inspect what's staged**

Run:
```bash
git status --short
```
Expected: M on the two test scripts, M on tools/assemble_payload.py, A on the three new test files, M on the SKILL.md files that needed edits, A on tools/__init__.py, A on tools/validate_payload.py, A on tools/post_to_n8n.py.

- [ ] **Step 2: Commit**

```bash
git commit -m "fix: update internal paths + add tools helpers after layout move

Phase 2-3 of the layout migration described in
docs/2026-05-12-repo-layout-design.md.

- Generalize tools/assemble_payload.py as a pure function
  parameterized over the three sub-payloads.
- Add tools/validate_payload.py (generic JSON Schema validator
  with cross-file \$ref support).
- Add tools/post_to_n8n.py (generic webhook POST with retries
  and optional archive).
- Add tools/__init__.py marker.
- Add pytest tests for all three tools modules.
- Update smoke_test.py and run_live.py to the new
  routines/weekly-ai-content/pipeline/* layout.
- Update SKILL.md files that referenced the old specs/* paths.

Both smoke_test.py and run_live.py confirmed green after the move."
```

- [ ] **Step 3: Verify**

Run:
```bash
git log --oneline -3
```
Expected: top commit is the one just made.

---

## Task 16: Write tools/README.md

**Files:**
- Create: `tools/README.md`

- [ ] **Step 1: Create file**

Create `tools/README.md`:

```markdown
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
```

- [ ] **Step 2: Stage**

Run:
```bash
git add tools/README.md
```

---

## Task 17: Write routines/weekly-ai-content/coordinator.md

**Files:**
- Create: `routines/weekly-ai-content/coordinator.md`

This is the entry point that the sandbox prompt will read.

- [ ] **Step 1: Create the coordinator**

Create `routines/weekly-ai-content/coordinator.md`:

```markdown
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
```

- [ ] **Step 2: Stage**

Run:
```bash
git add routines/weekly-ai-content/coordinator.md
```

---

## Task 18: Write routines/weekly-ai-content/README.md

**Files:**
- Create: `routines/weekly-ai-content/README.md`

- [ ] **Step 1: Create file**

Create `routines/weekly-ai-content/README.md`:

```markdown
# weekly-ai-content

A Claude Code routine that produces, every Friday, an AI industry
intelligence package and dispatches it to n8n for email + LinkedIn
distribution.

## What it does

1. Researches the last 7 days of frontier-lab activity across Anthropic,
   OpenAI, Google, xAI, plus the agent/dev/repo ecosystem.
2. Writes a structured email newsletter from that research.
3. Writes a LinkedIn post in Alan Vazquez's voice from the same research.
4. Bundles all three into a single JSON payload and POSTs it to n8n.

## Sandbox prompt

```
Clone github.com/alanvaa06/battle_tested_skills.
cd routines/weekly-ai-content.
Read coordinator.md and execute it.
```

## Required environment variables

| Variable | Required? | Notes |
|---|---|---|
| `WEEKLY_AI_WEBHOOK_URL` | yes | n8n webhook URL |
| `WEEKLY_AI_ARCHIVE_DIR` | no | defaults to `~/ai-pipeline-archive` |
| `WEEKLY_AI_LANGUAGE` | no | defaults to `English` |
| `WEEKLY_AI_REGION_FOCUS` | no | defaults to `Global` |

## Files

| Path | Role |
|---|---|
| `coordinator.md` | Entry point — Claude reads + executes |
| `skills/weekly-ai-research/` | Step 1: research |
| `skills/email-newsletter-ai/` | Step 2a: newsletter writer |
| `skills/linkedin-alan-post/` | Step 2b: LinkedIn writer |
| `pipeline/schemas/` | JSON Schemas for the three sub-payloads + final |
| `pipeline/fixtures/synthetic/` | Canned examples for offline tests |
| `pipeline/fixtures/live/` | Last real run (replay/debug) |
| `pipeline/tests/smoke_test.py` | Offline schema chain test |
| `pipeline/tests/run_live.py` | End-to-end runner against live fixtures |

## Running manually

```bash
# 1. Set env vars
export WEEKLY_AI_WEBHOOK_URL="https://n8n.alanvaa.cloud/webhook/provex-ai-news-weekly"

# 2. Open coordinator in Claude Code, follow steps.
# OR just run the offline smoke test:
python routines/weekly-ai-content/pipeline/tests/smoke_test.py
```

## Schedule

Friday 07:00 America/Mexico_City. Scheduled remote agent invocation
(configured outside this repo).
```

- [ ] **Step 2: Stage**

Run:
```bash
git add routines/weekly-ai-content/README.md
```

---

## Task 19: Write the root README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create file**

Create `README.md` at the repo root:

```markdown
# battle_tested_skills

Reproducible Claude Code routines. Each routine is a self-contained
workflow that a sandbox can clone, open, and execute end-to-end.

## Layout

```
battle_tested_skills/
├── routines/             # one folder per routine
├── tools/                # generic, parameterized helpers shared across routines
├── docs/                 # design specs, plans, architecture
└── README.md             # this file
```

## Routine index

| Routine | Purpose | Payload? | Schedule |
|---|---|---|---|
| `weekly-ai-content` | Weekly AI industry digest → email + LinkedIn | yes (JSON to n8n) | Friday 07:00 America/Mexico_City |

## How to run a routine

The sandbox prompt is always:

```
Clone github.com/alanvaa06/battle_tested_skills.
cd routines/<routine-name>.
Read coordinator.md and execute it.
```

The routine's `README.md` documents required environment variables. The
`coordinator.md` is what Claude actually executes — read it to understand
the work, or run it directly.

## Conventions

- **Per-routine isolation.** Each routine owns its `skills/` and (when
  applicable) `pipeline/`. Skills are not shared between routines.
- **Generic plumbing in `tools/`.** HTTP POST, schema validation, payload
  assembly. Tools take parameters and never hardcode routine-specific
  field names.
- **Coordinator is the entry point.** Single file per routine. Claude
  reads it as a prompt.
- **Env vars at sandbox spawn.** Secrets and config arrive as environment
  variables, never committed to the repo.
- **JSON Schema 2020-12.** All payload contracts live under
  `routines/<r>/pipeline/schemas/`.

## Adding a new routine

1. `mkdir -p routines/<new-name>/skills`.
2. Add `coordinator.md` + `README.md`.
3. If the routine emits a JSON payload, create `pipeline/{schemas,fixtures,tests}`.
4. Copy any required skills into `routines/<new-name>/skills/` (full
   copies — no symlinks).
5. Append a row to the Routine index above.

## Spec + plan

- Design: `docs/2026-05-12-repo-layout-design.md`
- Implementation plan: `docs/2026-05-12-repo-layout-plan.md`
```

- [ ] **Step 2: Stage**

Run:
```bash
git add README.md
```

---

## Task 20: Write .gitignore

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Create file**

Create `.gitignore` at the repo root:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/
*.egg-info/

# Editor / OS
.vscode/
.idea/
.DS_Store
Thumbs.db

# Secrets (never commit)
.env
.env.*
*.pem
*.key

# Per-routine live fixtures policy
# Keep the most recent run committed for replay; let older runs rotate.
# (Adjust per routine as needed — currently nothing excluded here.)
```

- [ ] **Step 2: Stage**

Run:
```bash
git add .gitignore
```

---

## Task 21: Commit new files (coordinator + READMEs + .gitignore + tools/README)

- [ ] **Step 1: Inspect staged**

Run:
```bash
git status --short
```
Expected: A on `tools/README.md`, `routines/weekly-ai-content/coordinator.md`, `routines/weekly-ai-content/README.md`, `README.md`, `.gitignore`.

- [ ] **Step 2: Commit**

```bash
git commit -m "feat: add coordinator, READMEs, gitignore for weekly-ai-content

Phase 3 of the layout migration. Adds the routine entry point
(coordinator.md), human-facing READMEs at three levels (routine,
tools, repo root), and a baseline .gitignore.

The coordinator now uses the generic tools/* helpers (assemble,
validate, post) instead of inline curl + Python."
```

---

## Task 22: Re-point Windows junctions in ~/.claude/skills/

**Files:**
- Replace: `~/.claude/skills/weekly-ai-research` junction
- Replace: `~/.claude/skills/email-newsletter-ai` junction
- Replace: `~/.claude/skills/linkedin-alan-post` junction

This task is the only one that affects state outside the repo. Do it in PowerShell.

- [ ] **Step 1: Confirm current junction state**

Run in PowerShell:

```powershell
$skills = "C:\Users\alanv\.claude\skills"
foreach ($n in @("weekly-ai-research","email-newsletter-ai","linkedin-alan-post")) {
    $p = "$skills\$n"
    if (Test-Path $p) {
        $item = Get-Item $p -Force
        Write-Output "$n -> $($item.LinkType) :: $($item.Target)"
    } else {
        Write-Output "$n -> MISSING"
    }
}
```

Expected: each `LinkType=Junction` pointing at `...\battle_tested_skills\<skill-name>` (the OLD root location).

- [ ] **Step 2: Drop old junctions**

```powershell
foreach ($n in @("weekly-ai-research","email-newsletter-ai","linkedin-alan-post")) {
    cmd /c rmdir "C:\Users\alanv\.claude\skills\$n"
}
```

Note: use `rmdir` (NOT `Remove-Item -Recurse`) — junctions must be removed without following the link, otherwise PowerShell traverses into the target.

- [ ] **Step 3: Re-create junctions to the new location**

```powershell
$base = "C:\Users\alanv\OneDrive\Documentos\GitHub\battle_tested_skills\routines\weekly-ai-content\skills"
foreach ($n in @("weekly-ai-research","email-newsletter-ai","linkedin-alan-post")) {
    cmd /c mklink /J "C:\Users\alanv\.claude\skills\$n" "$base\$n" | Out-Null
    $item = Get-Item "C:\Users\alanv\.claude\skills\$n" -Force
    Write-Output "$n -> $($item.LinkType) :: $($item.Target)"
}
```

Expected: three lines, each `LinkType=Junction`, `Target=...routines\weekly-ai-content\skills\<n>`.

- [ ] **Step 4: Read a SKILL.md through the junction to confirm**

Run in PowerShell:

```powershell
Get-Content "C:\Users\alanv\.claude\skills\weekly-ai-research\SKILL.md" -TotalCount 5
```

Expected: opens cleanly with `---\nname: weekly-ai-research\n...`.

No git operation in this task.

---

## Task 23: Verify end-to-end after the move

- [ ] **Step 1: Run smoke test on synthetic fixtures**

Run:
```bash
python routines/weekly-ai-content/pipeline/tests/smoke_test.py
```
Expected: ends with `CHAIN INTEGRITY: all 4 schemas validated, payload assembled cleanly.`

- [ ] **Step 2: Run the live runner**

Run:
```bash
python routines/weekly-ai-content/pipeline/tests/run_live.py
```
Expected: ends with `CHAIN INTEGRITY: all 4 schemas validated on LIVE data.`

- [ ] **Step 3: Run all pytest tests**

Run:
```bash
python -m pytest routines/weekly-ai-content/pipeline/tests -v
```
Expected: 10 tests pass (4 validate + 4 post + 1 assemble + at least one if test discovery picks up smoke/live).

- [ ] **Step 4: Confirm working tree is clean**

Run:
```bash
git status --short
```
Expected: empty.

- [ ] **Step 5: Show final commit log**

Run:
```bash
git log --oneline -8
```
Expected (top three):
```
<hash> feat: add coordinator, READMEs, gitignore for weekly-ai-content
<hash> fix: update internal paths + add tools helpers after layout move
<hash> refactor: move to routines/* + tools/* layout
```

---

## Task 24: Pause before push

This plan deliberately does **not** push. Direct push to `main` requires explicit user authorization per the harness hook rules. After Task 23 passes, report back with the four pending commits and ask for the explicit phrase:

> "yes, push commits <h1> <h2> <h3> <h4> to origin/main on the private repo battle_tested_skills"

(The fourth hash is the pre-existing `dbb36af` design-spec commit.)

Then run:

```bash
git push origin main
```

Verify:

```bash
git log --oneline origin/main -8
```
Expected: matches local `main`.

---

## Out of scope (deferred)

- Versioning routines (no tags, no changelog).
- CI workflows under `.github/`.
- A second routine (e.g. `morning-note`).
- Vault-based secrets fetch.
- Live-fixture rotation policy (currently committed verbatim).
- Coordinator markdown linter.

These are listed in the spec under "Open Questions" and will be picked up
as separate, smaller plans when the need arrives.
