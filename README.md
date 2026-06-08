# battle_tested_skills

Open-source [Claude Code](https://claude.com/claude-code) skills for the
**CFA / quant community** — battle-tested helpers for investment research,
strategy stress-testing, and disciplined agentic engineering. Each skill is
self-contained: clone it, drop it into your Claude Code `skills/` directory,
and go.

## Skills

| Skill | What it does | Audience |
|---|---|---|
| [`roast-me`](roast-me/) | Coach-mode Socratic challenger that stress-tests an investment thesis, signal logic, backtest, or config. Runs a required quant-guardrail checklist (lookahead, survivorship, leakage, costs, overfitting) and ends with a written red-flag summary plus prioritized next moves. | CFA charterholders, quants, engineers |
| [`scaffold`](scaffold/) | Agentic project template — a `CLAUDE.md` senior-engineer persona plus a `docs/` context structure (memory, lessons, todo, session-log, PRD, references) for plan-first, self-improving, verification-driven workflows. | Anyone building with Claude Code |

## Install a skill

Copy the skill folder into your Claude Code skills directory:

```bash
# Personal (all projects)
cp -r roast-me ~/.claude/skills/roast-me

# Or per-project
cp -r roast-me .claude/skills/roast-me
```

Claude discovers the skill from its `SKILL.md` and triggers it from the
`description`. `scaffold` is a project template — copy its `CLAUDE.md` and
`docs/` into a new repo root to start a project with the persona and context
files in place.

## Skill anatomy

```
<skill-name>/
├── SKILL.md          # name + description frontmatter, then instructions
└── references/       # optional deeper material loaded on demand
```

## Contributing

This is a community container — PRs adding or improving skills are welcome.
Keep each skill self-contained, give it a clear trigger `description`, and add
a row to the Skills table above.

> Nothing here is investment advice.
