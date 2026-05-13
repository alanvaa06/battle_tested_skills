# battle_tested_skills

Reproducible Claude Code routines. Each routine is a self-contained
workflow that a sandbox can clone, open, and execute end-to-end.

## Layout

```
battle_tested_skills/
├── routines/             # one folder per routine
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
Read SCHEDULED_PROMPT.md and execute it.
```

The routine's `README.md` documents required environment variables. The
`SCHEDULED_PROMPT.md` is what Claude actually executes — read it to understand
the work, or run it directly.

## Conventions

- **Per-routine isolation.** Each routine owns its `skills/`. Skills are not shared between routines.
- **Routines are self-contained** — everything they need lives under `routines/<name>/`.
- **SCHEDULED_PROMPT.md is the entry point.** Single file per routine. Claude reads it as a prompt.
- **Env vars at sandbox spawn.** Secrets and config arrive as environment variables, never committed to the repo.

## Adding a new routine

1. `mkdir -p routines/<new-name>/skills`.
2. Add `SCHEDULED_PROMPT.md` + `README.md`.
3. Include all required skills directly under `routines/<new-name>/skills/`.
4. Append a row to the Routine index above.

## Spec + plan

- Design: `docs/2026-05-12-repo-layout-design.md`
- Implementation plan: `docs/2026-05-12-repo-layout-plan.md`
