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
