# {{PROJECT_NAME}} — Claude Code instructions

## System Persona

{{SYSTEM_PERSONA}}

## Context files — read ON DEMAND, never bulk-read

`docs/context/` is the project's working memory: `memory.md` (architecture decisions), `lessons.md` (past mistakes → rules), `todo.md` (open work), `results.md` (build log), `sesion-log.md` (session history). These are reference, **not a boot sequence**. Bulk-reading all of them every task wastes thousands of tokens — DON'T.

- **Trivial / single-file task**: skip the context files entirely.
- **Non-trivial task**: `grep` the relevant file(s) for keywords tied to what you're touching (module, agent, symbol, feature) and read only the matching lines. Full-read a file only when its whole content is genuinely on-topic.
- **Before a fix**: grep `lessons.md` for the area — you may have hit it before.
- **When starting work**: check `todo.md` for the matching item and update its status (`pending` → `in_progress` → `done`).

## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for **ANY** non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, **STOP** and re-plan immediately — don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- One task per subagent for focused execution
- **Subagents don't inherit the conversation.** When dispatching one, paste the relevant lines from `memory.md`/`lessons.md` into its prompt — it can't know decisions it never saw.
- A `SubagentStop` hook auto-appends each subagent's final line to `results.md`; distill anything load-bearing into `memory.md` yourself.

### 3. Self-Improvement Loop
- After **ANY** correction from the user: update `docs/context/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them

## Task Management

1. **Write Plan**: Write plan phases to `docs/context/todo.md`. Todo format, one line per item.
2. **Document Results**: Add a review line to `docs/context/results.md` — keep readable, 1 to 4 lines. List format.
3. **Capture Lessons**: Update `docs/context/lessons.md` after a correction. List format. Friction only — if everything is a lesson, nothing is.
4. **Update memory**: When finishing a task or settling an architecture decision of high relevance, write to `docs/context/memory.md`: `# decision: sentence`. One line, readable. List format.
5. **Session-log**: After completing a major task or wrapping up a work block, append to `docs/context/sesion-log.md`: `[date]: information`. One line. (A `SessionEnd` hook writes a bare date stub automatically when you didn't — your line carries the substance, don't rely on the stub.)
6. **Context files have HARD CAPS — enforced by hook + `/compact-context`.** Cap values live in ONE place: `.claude/hooks/context-size-check.ps1` — never restate them here or elsewhere. That `UserPromptSubmit` hook stats the files every turn; **when you see `[context-size] OVER CAP`, run `/compact-context`** — it snapshots the file to `docs/context/archive/<file>/<date>.md`, then hard-compacts the active file in place. Day-to-day: one line per entry, no prose, dedupe before appending (never restate an existing fact); `todo.md` holds ONLY `pending`/`in_progress` (done → `results.md` → archive). Don't compact inline during feature work — that's what the command is for.

## References & Skills

- Coding and design standards live in global skills, not in this file: `python-standards` fires on any Python work; agent/pipeline work is covered by the agent-cycle plugin's skills. Follow them when they trigger.
- `docs/references/` holds **project-specific** reference material only (domain specs, API notes). Read on demand when the task touches that domain.
- Product requirement docs live in `docs/prd/` as `NNN-feature-name.md`.

## Core Principles

* **Simplicity First**: Make every change as simple as possible. Touch minimal code.
* **No Laziness**: Find root causes. No temporary fixes. Senior standards.
* **Minimal Impact**: Changes touch only what's necessary. Don't introduce new bugs.
