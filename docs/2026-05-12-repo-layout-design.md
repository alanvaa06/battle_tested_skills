# Repo Layout for Claude Code Routines — Design

**Date:** 2026-05-12
**Repo:** `battle_tested_skills`
**Status:** Approved (brainstorm complete, ready for implementation plan)
**Owner:** Alan Vazquez

---

## Problem

`battle_tested_skills` started as a flat repo containing three skills (`weekly-ai-research`, `linkedin-alan-post`, `email-newsletter-ai`) and a `specs/` directory holding JSON Schemas, fixtures, and smoke tests for a single content pipeline. The pipeline currently works end-to-end (live POST to `https://n8n.alanvaa.cloud/webhook/provex-ai-news-weekly` succeeded with HTTP 200, Gmail message delivered).

The repo now needs to host multiple **routines** — sequenced workflows that Claude Code executes in a sandbox. Each routine is invoked by a scheduled remote agent that clones the repo, opens the routine's coordinator, and follows its instructions. Some routines emit JSON payloads to webhooks; others output markdown or perform side effects without a payload contract.

The flat layout does not scale to multiple routines, and the existing skills, schemas, and fixtures are scattered across the root.

## Goals

- Make each routine self-contained and reproducible from a sandbox clone.
- Keep skills isolated per routine so changes do not cascade across unrelated work.
- Share boring plumbing (HTTP, JSON Schema validation, payload assembly) without leaking domain logic.
- Support routines with and without JSON payload contracts under the same convention.
- Preserve existing `~/.claude/skills/` junctions and the green smoke test.

## Non-Goals

- Versioning routines (deferred).
- CI/CD workflows (deferred to a follow-up).
- A second routine (`morning-note`, `equity-update`, etc.) — captured as future work, not in this migration.
- A vault-based secrets manager — env vars at sandbox spawn are sufficient for now.
- Backward-compatible aliases at old paths — junctions will be re-pointed in one step.

## Decisions (Brainstorm Log)

The seven decisions that shaped this design, with the reasoning behind each.

| # | Decision | Rationale |
|---|----------|-----------|
| Q1 | Coordinators only; no sub-agents | A `coordinator.md` per routine orchestrates skills via `Skill()` calls. Sub-agents add complexity without solving a current problem. |
| Q2 | Strict per-routine skill isolation | Every routine ships its own `skills/` subtree. Duplication is accepted in exchange for full sandbox reproducibility and no cross-routine breakage. |
| Q3 | `pipeline/` subdir for JSON-payload work | Routines that emit a payload group schemas, fixtures, and tests under `pipeline/`. Routines without payloads omit the directory entirely. |
| Q4 | `coordinator.md` is the entry point | The sandbox prompt is "open this routine's coordinator and execute it." No runner script. Claude is the runner. |
| Q5 | Shared `tools/` at the repo root | Generic plumbing (HTTP POST, schema validation, payload assembly) lives at the root. Tools take parameters; they do not encode routine-specific policy. |
| Q6 | External deps declared imperatively in coordinator prose | Coordinator instructs Claude to clone, install, and run external code. No separate manifest required. |
| Q7 | Secrets via env vars at sandbox spawn | Scheduler sets `WEEKLY_AI_WEBHOOK_URL`, `FACTSET_API_KEY`, etc. Coordinator reads them directly. Documented per-coordinator. |

## Architecture

### Top-level layout

```
battle_tested_skills/
├── README.md                       # repo intro + routine index
├── tools/                          # shared generic plumbing
│   ├── post_to_n8n.py
│   ├── validate_payload.py
│   ├── assemble_payload.py
│   └── README.md
├── routines/
│   ├── weekly-ai-content/          # routine with JSON payload
│   └── morning-note/               # example of a routine without payload (future)
├── docs/
│   └── 2026-05-12-repo-layout-design.md
├── .gitignore
└── .github/                        # CI workflows (later)
```

### Anatomy of a routine with a payload

```
routines/weekly-ai-content/
├── README.md
├── coordinator.md                  # entry point — Claude reads + executes
├── skills/
│   ├── weekly-ai-research/SKILL.md
│   ├── email-newsletter-ai/SKILL.md
│   └── linkedin-alan-post/SKILL.md
└── pipeline/
    ├── schemas/                    # JSON Schema 2020-12
    │   ├── research_output.schema.json
    │   ├── newsletter_output.schema.json
    │   ├── linkedin_output.schema.json
    │   └── final_payload.schema.json
    ├── fixtures/
    │   ├── synthetic/              # canned examples, committed
    │   └── live/                   # last real run; gitignore older runs
    └── tests/
        ├── smoke_test.py
        └── run_live.py
```

### Anatomy of a routine without a payload

```
routines/morning-note/
├── README.md
├── coordinator.md
└── skills/
    └── morning-note-writer/SKILL.md
```

No `pipeline/`. Coordinator may still import `tools/post_to_n8n.py` if it dispatches to a webhook, but no schema or fixture artifacts are required.

### How tools/ stays generic

`tools/` modules accept the routine's data and schema paths as parameters; they never hardcode field names from any specific payload.

- `tools/post_to_n8n.py` — given `payload: dict`, `webhook_url: str`, `archive_path: Path | None`, performs the POST with retries and optional archiving. Returns `{status, http_code, response, attempts}`.
- `tools/validate_payload.py` — given `payload: dict`, `schema_path: Path`, `schemas_dir: Path | None`, validates with cross-file `$ref` resolution via the `referencing` registry.
- `tools/assemble_payload.py` — given `research_output`, `newsletter_output`, `linkedin_output` dicts (or other sub-payloads), composes the `final_payload` shape declared by the caller. Routine-specific assemblers can be added as sibling modules if shapes diverge.

Policy lives in each routine: which fields exist, which schema validates them, which webhook receives them, which env vars carry the secrets.

### Coordinator structure

Each coordinator follows a six-step shape, scaled to the routine's complexity:

1. **Required env vars** — documented at the top.
2. **Skill invocations** — sequence of `Skill()` calls with `pipeline_mode: true` and any inputs.
3. **Validation gates** — after each skill, validate output against the relevant schema; re-prompt once on failure, then abort.
4. **Assembly** — call into `tools/assemble_payload.py` to compose the final payload.
5. **Dispatch** — `tools/post_to_n8n.py` with the routine's webhook URL.
6. **Report** — print a terminal summary (week_ref, http_code, bullet_count, pattern_used, archive path).

### Sandbox execution model

```
1. Scheduled remote agent fires.
2. Sandbox spawns with env vars set (WEEKLY_AI_WEBHOOK_URL, etc.).
3. Sandbox prompt: "Clone github.com/alanvaa06/battle_tested_skills.
   cd routines/<name>. Read coordinator.md and execute it."
4. Claude reads coordinator.md, follows steps, invokes skills,
   calls into tools/, POSTs to webhook.
5. n8n persists outputs (email sent, LinkedIn drafted, archive written).
6. Sandbox tears down. Last-run snapshot may be pushed back to
   routines/*/pipeline/fixtures/live/ if desired.
```

## Migration Plan

Six phases, each ending in a commit. Push happens at the end with explicit authorization per hook rules.

### Phase 1 — Move files (history-preserving)

```bash
mkdir -p routines/weekly-ai-content/skills
mkdir -p routines/weekly-ai-content/pipeline/{schemas,fixtures/synthetic,fixtures/live,tests}
mkdir -p tools docs

git mv weekly-ai-research    routines/weekly-ai-content/skills/
git mv email-newsletter-ai   routines/weekly-ai-content/skills/
git mv linkedin-alan-post    routines/weekly-ai-content/skills/

git mv specs/research_output.schema.json   routines/weekly-ai-content/pipeline/schemas/
git mv specs/newsletter_output.schema.json routines/weekly-ai-content/pipeline/schemas/
git mv specs/linkedin_output.schema.json   routines/weekly-ai-content/pipeline/schemas/
git mv specs/final_payload.schema.json     routines/weekly-ai-content/pipeline/schemas/

git mv specs/fixtures/research_output.example.json   routines/weekly-ai-content/pipeline/fixtures/synthetic/
git mv specs/fixtures/newsletter_output.example.json routines/weekly-ai-content/pipeline/fixtures/synthetic/
git mv specs/fixtures/linkedin_output.example.json   routines/weekly-ai-content/pipeline/fixtures/synthetic/
git mv specs/fixtures/final_payload.example.json     routines/weekly-ai-content/pipeline/fixtures/synthetic/
git mv specs/fixtures/live/* routines/weekly-ai-content/pipeline/fixtures/live/

git mv specs/fixtures/smoke_test.py routines/weekly-ai-content/pipeline/tests/
git mv specs/fixtures/run_live.py   routines/weekly-ai-content/pipeline/tests/

git mv specs/fixtures/assemble_payload.py tools/assemble_payload.py

rmdir specs/fixtures/live specs/fixtures specs
```

Commit: `refactor: move to routines/* + tools/* layout`

### Phase 2 — Fix internal path references

- `tools/assemble_payload.py` — parameterize input/output paths; remove hardcoded ROOT logic.
- `routines/weekly-ai-content/pipeline/tests/smoke_test.py` — point to new schema/fixture paths.
- `routines/weekly-ai-content/pipeline/tests/run_live.py` — same.
- Each `SKILL.md` — update internal references from `specs/...` to relative `pipeline/...` paths where mentioned.

Commit: `fix: update path references after layout move`

### Phase 3 — New files

- `tools/post_to_n8n.py` — extracted from the existing coordinator's curl block; generic POST with retries + optional archive.
- `tools/validate_payload.py` — extracted helper with `$ref` registry support.
- `tools/README.md` — function signatures and usage examples.
- `routines/weekly-ai-content/coordinator.md` — port of the existing coordinator prompt, updated for new paths.
- `routines/weekly-ai-content/README.md` — required env vars, how to run manually, scheduled cadence.
- Root `README.md` — repo overview, routine index, conventions link.

Commit: `feat: add coordinator, tools, and routine README for weekly-ai-content`

### Phase 4 — Re-point `~/.claude/skills/` junctions

```
~/.claude/skills/weekly-ai-research   → routines/weekly-ai-content/skills/weekly-ai-research
~/.claude/skills/email-newsletter-ai  → routines/weekly-ai-content/skills/email-newsletter-ai
~/.claude/skills/linkedin-alan-post   → routines/weekly-ai-content/skills/linkedin-alan-post
```

Drop old junctions, recreate with `mklink /J`.

### Phase 5 — Verify

```
python routines/weekly-ai-content/pipeline/tests/smoke_test.py
python routines/weekly-ai-content/pipeline/tests/run_live.py
ls ~/.claude/skills/weekly-ai-research/SKILL.md
```

All three must pass before pushing.

### Phase 6 — Push

Three commits to `origin/main` after explicit push authorization.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Path edits miss a reference, tests fail | Phase 2 enumerates the files; Phase 5 catches misses |
| Junctions break, skills disappear from `~/.claude/skills/` | Phase 4 re-points; Phase 5 verifies |
| `git mv` loses history when combined with content edits | Moves in Phase 1, edits in Phase 2 — never in the same commit |
| Live fixtures (real research data) accidentally committed | `pipeline/fixtures/live/.gitignore` keeps only the most recent run, or all runs are gitignored entirely |
| Sandbox prompt diverges from coordinator structure | Coordinator README at top documents the contract; root README lists conventions |

## Conventions

- **Routine name** — kebab-case, descriptive verb-or-domain (`weekly-ai-content`, `morning-note`, `equity-update-mexico`). No abbreviations.
- **Skill name** — kebab-case (`weekly-ai-research`). Skill directory contains exactly one `SKILL.md` plus optional `references/`.
- **Schema file name** — `<object_name>.schema.json`, JSON Schema 2020-12.
- **Fixture file name** — `<object_name>.example.json` (synthetic) or `<object_name>.json` (live).
- **Env var name** — SCREAMING_SNAKE prefixed by routine or scope (`WEEKLY_AI_WEBHOOK_URL`, not `WEBHOOK_URL`).
- **Tools function** — pure, parameterized, schema-agnostic; never hardcodes routine field names.
- **Coordinator filename** — always `coordinator.md` at the routine root.

## Open Questions (Deferred)

- Versioning per routine (semver tags? changelog file? do nothing?).
- Whether live fixtures are committed back to the repo from the sandbox or stay ephemeral.
- CI workflow on push: run all routine smoke tests, validate all schemas.
- Cron mechanism for triggering sandbox runs (claude.ai scheduled remote agents vs. external scheduler).

## Next Step

Invoke the `superpowers:writing-plans` skill to convert this design into an executable implementation plan.
