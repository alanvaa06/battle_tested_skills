---
name: scaffold
description: Verify or create a project's context system — a docs/context/ working memory (memory, lessons, todo, results, sesion-log), a CLAUDE.md that reads it ON DEMAND (never bulk), hard size caps enforced by a UserPromptSubmit hook + /compact-context command, state-capture hooks (SubagentStop, SessionEnd, PreCompact), companion skills (python-standards, excel-standards), and a project-specific system persona. Idempotent: brings a project up to the convention and no-ops if it already conforms. Use whenever the user says "scaffold", "set up the context system", "add the docs/context convention", "wire up the caps hook", "initialize CLAUDE.md", or starts work in a repo that has no docs/context/ or a CLAUDE.md missing the on-demand-read convention.
disable-model-invocation: true
---

# Project Scaffold — verify or create

Idempotent. Brings the current project up to the **context-system convention** and changes nothing if it already conforms. Run it on a fresh repo to set everything up, or on an existing one to check and fill only the gaps.

The convention has one core idea: `docs/context/` is durable working memory that is read **on demand**, not bulk-loaded every turn, and is kept small by **hard caps** that a hook watches and a `/compact-context` command enforces. State-capture hooks make the memory survive what the model forgets: `SubagentStop` appends each subagent's final line to `results.md`, `SessionEnd` stubs `sesion-log.md` when no entry was written, `PreCompact` marks compaction points. CLAUDE.md teaches the project's Claude to use it all under a project-specific persona. Coding/design standards live in companion **skills** (`python-standards`, `excel-standards`), not in CLAUDE.md prose; agent work is covered by the agent-cycle plugin — skill descriptions trigger structurally; CLAUDE.md read-this-file instructions degrade over long sessions.

Templates live in `./templates/` next to this SKILL.md (resolve relative to the skill's own directory). Treat them as source — DO NOT modify them; copy out of them.

**Cap values have ONE source of truth: `.claude/hooks/context-size-check.ps1` (`$caps` table).** CLAUDE.md and `/compact-context` point at it instead of restating numbers — when auditing, flag any file that hardcodes cap values elsewhere as non-conforming (drift hazard).

## Hook contract — a write-capable hook must prove its trigger fired

State-capture hooks append to the user's working memory on every event. A hook that cannot tell a real event from an ambient one silently poisons `results.md`, and the damage is invisible until someone reads the file weeks later.

**The rule: derive the guard from a field that is only populated for the real event, and exit when it is absent. Never substitute a default for missing identity.**

`subagent-capture.ps1` is the cautionary case. Some runtimes fire `SubagentStop` on **every main-agent turn**, not only after a real subagent. Observed payload from a plain turn where no subagent ran (2026-07-31, Claude Code on Windows):

```json
{"session_id":"…","agent_id":"a347c5176b08fade6","agent_type":"",
 "hook_event_name":"SubagentStop","last_assistant_message":"<the user's own prompt>"}
```

Two traps in one payload:

- `agent_id` **is** populated, so gating on "any identity field" still logs ordinary turns. Only a non-empty **`agent_type`** distinguishes a real subagent.
- `last_assistant_message` carries the **user's** text, so the logged line looks like a transcript leak, not agent output.

The original template did `if ($data.agent_type) { … } else { 'subagent' }`. That `else` turned missing identity into a plausible value, so the script never got to ask whether a subagent had run — it just wrote. One project accumulated 23 junk lines before anyone noticed. When auditing, a `subagent-capture.ps1` that lacks the non-empty-`agent_type` gate is **non-conforming**, and `results.md` lines matching `subagent subagent:` are contamination, not history.

Corollary for any hook added later: write UTF-8 explicitly (`[System.IO.File]::AppendAllText` with `UTF8Encoding`), because `Add-Content` defaults to ANSI and mangles accented text into `implementaci??n`.

## Templates layout (source)

```
templates/
  CLAUDE.md                       # {{PROJECT_NAME}} + {{SYSTEM_PERSONA}} tokens
  .claude/
    settings.json                 # registers all four hooks below
    hooks/
      context-size-check.ps1      # UserPromptSubmit — warns when a context file is over cap (caps table lives here)
      subagent-capture.ps1        # SubagentStop — appends subagent final line to results.md
      session-end-log.ps1         # SessionEnd — date stub in sesion-log.md if no entry today
      precompact-log.ps1          # PreCompact — compaction marker in sesion-log.md
    commands/compact-context.md   # /compact-context — snapshot + hard-compact
  skills/
    python-standards/             # fallback copies — install ONLY if not in ~/.claude/skills/
    excel-standards/              # domain: Excel/financial-model work
  docs/
    context/{memory,lessons,todo,results,sesion-log}.md
    prd/README.md
```

## What "compliant" means — the checklist

A project conforms when ALL of these hold. Use this same list to audit (Step 1) and to verify (Step 6).

1. `docs/context/` contains: `memory.md`, `lessons.md`, `todo.md`, `results.md`, `sesion-log.md`.
2. `CLAUDE.md` exists and carries the convention markers:
   - the string `read ON DEMAND` (the on-demand context rule),
   - a `## Task Management` section,
   - the string `HARD CAPS` (the caps rule — pointing at the hook, NOT restating values),
   - a `## Workflow Orchestration` section (plan mode, subagent strategy incl. the paste-context rule, self-improvement loop).
3. `CLAUDE.md` has a non-empty `## System Persona` section (default or custom both count).
4. All four hook scripts exist under `.claude/hooks/`: `context-size-check.ps1`, `subagent-capture.ps1`, `session-end-log.ps1`, `precompact-log.ps1`.
   - `subagent-capture.ps1` gates on a **non-empty `agent_type`** and exits otherwise (see *Hook contract* above). A copy that falls back to a default agent name, or that accepts `agent_id` as identity, is **non-conforming** — it logs ordinary turns.
   - `results.md` contains no lines matching `subagent subagent:` — those are contamination from the buggy gate, not history. Lines with a real agent name (`subagent Explore:`, `subagent general-purpose:`) are genuine and must be preserved.
5. `.claude/commands/compact-context.md` exists.
6. `.claude/settings.json` registers all four hook events (`UserPromptSubmit`, `SubagentStop`, `SessionEnd`, `PreCompact`) with commands referencing the scripts above.
7. Skills `python-standards` and `excel-standards` are available: present in `~/.claude/skills/` (preferred) **or** in the project's `.claude/skills/`. Global presence satisfies this — do NOT also install project copies (double registration = duplicate triggering).

Note the deliberate spelling `sesion-log.md` (one `s`) — the hooks key on that exact name, so don't "correct" it.

## Step 1 — Audit (read before you write)

Check every checklist item against the current working directory (for item 7, also check `~/.claude/skills/`). Produce a short table: each item `present` / `missing` / `non-conforming`. **Report it before changing anything.**

If every item is present and conforming → say so plainly and stop. This is a true no-op: don't re-run the persona interview, don't rewrite files, don't reformat. An already-scaffolded repo should cost the user nothing.

## Step 2 — Persona interview (only when creating or repairing CLAUDE.md)

Run this ONLY if `CLAUDE.md` is missing, or its `## System Persona` section is absent/empty. Skip it entirely when CLAUDE.md already has a persona — re-asking on a conforming repo is the failure mode to avoid.

Keep it short — 2-3 questions, one at a time, then write. Ask:

1. **Domain** — what does this project build? (one line)
2. **Role** — what persona should its Claude adopt? Offer the default and let the user accept or replace it:
   > Default: *Senior AI Software Engineer — multi-agent systems, LLM orchestration, agentic pipelines.* Keep it, or describe a different role?
3. **Standards** — any non-negotiables to bake in (test framework, stack conventions, review bar)?

Assemble the answers into the persona text. If the user just says "default", use this verbatim:

```
You are a **Senior AI Software Engineer** with deep expertise in multi-agent systems, LLM orchestration, and modern software architecture, capable of designing and orchestrating autonomous pipelines.

- Apply rigorous engineering standards: modularity, clean architecture, maintainability.
- Communicate with precision — correct terminology for agentic patterns (ReAct, RAG, Tool Use, StateGraph).
- Weigh trade-offs between latency, token cost, and accuracy explicitly.
- Distinguish verified facts from inference; flag assumptions.
```

## Step 3 — Create the missing pieces (per-file conflict policy)

For each item the audit marked `missing`, copy it from `templates/` to the same relative path under the cwd (Read the template, Write the target). For `CLAUDE.md`, before writing, replace the tokens:
- `{{PROJECT_NAME}}` → the repo/working-dir name.
- `{{SYSTEM_PERSONA}}` → the Step 2 persona text.

**Skills (checklist item 7) are the exception to "same relative path":** if a skill is missing both globally and in the project, copy `templates/skills/<name>/` to the **project's** `.claude/skills/<name>/`. If it exists globally, do nothing — never create a project copy alongside a global one.

For items the audit marked **`non-conforming`** (the file exists but is wrong — e.g. a CLAUDE.md with no on-demand rule, a CLAUDE.md that hardcodes cap values, or `settings.json` with other hooks but not these), do NOT silently overwrite. Ask:

```
Found existing <path>, non-conforming. Options:
  [k] keep — leave as-is (you reconcile by hand)
  [o] overwrite — replace with the scaffold version
  [m] merge — splice the missing convention in, preserve the rest
Choice? (default: keep)
```

- **CLAUDE.md merge** = insert the missing sections (on-demand rule, Workflow Orchestration, Task Management, caps-pointer) without disturbing the user's existing persona/content; replace any hardcoded caps table with the pointer to the hook.
- **settings.json merge** = add the missing hook-event entries to the existing `hooks` object; never clobber other hooks or settings.

## Step 4 — Existing project: prefill the new context files (optional)

Run ONLY on context files this invocation just created, on a repo that already has source (skip for an empty/new repo, and skip files the user kept). Goal: the working memory starts with real signal, not stubs.

Scan the repo (use an Explore subagent if large), in parallel:
1. **Stack** — `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, `*.csproj`, `Gemfile`, `composer.json`.
2. **Architecture** — top-level dirs, one-line role each; entrypoints (`main.py`, `index.ts`, `cli.py`, server bootstrap).
3. **Recent work** — `git log --oneline -30` if git.
4. **TODOs** — grep `TODO|FIXME|HACK|XXX`, cap 50 hits.

Then replace `*(empty)*`:
- `memory.md` — evidenced decisions, mark uncertain ones `(inferred)`: `# stack: <lang> + <framework>.` / `# architecture: <pattern>.` / `# entrypoint: <path>.` / `# testing: <framework or "none found">.`
- `sesion-log.md` — `[<TODAY-ISO>]: scaffold initialized. Stack=<x>, entrypoints=<y>, themes=<z>.`
- `lessons.md` — only if git log shows fix/revert/hotfix patterns, max 3.
- `todo.md` — seed grepped TODOs as `pending`, max 20: `- [ ] [pending] <file:line> — <text>`.

Respect the caps — keep prefill well under each file's budget.

## Step 5 — Migrate legacy references (existing projects only)

If the project has `docs/references/python_best_practices.md` or `docs/references/agent-design-best-practices.md` (pre-skill convention), tell the user those are superseded by the `python-standards` skill and the agent-cycle plugin and offer to delete them. Any CLAUDE.md line instructing "read docs/references/<those files>" is non-conforming — remove it during the Step 3 merge (the References & Skills section replaces it). Project-specific references stay.

## Step 6 — Verify + report

Re-run the Step 1 checklist. Confirm every item now `present`/`conforming`.

**Smoke-test `subagent-capture.ps1` before reporting.** It is the only hook that writes user-visible content on someone else's trigger, and a broken gate is silent. Feed it two synthetic payloads and check `results.md`:

```powershell
$before = (Get-Content docs\context\results.md).Count
# 1. ambient turn — MUST NOT write
'{"hook_event_name":"SubagentStop","agent_id":"x","agent_type":"","last_assistant_message":"hola"}' |
  powershell -NoProfile -ExecutionPolicy Bypass -File .claude\hooks\subagent-capture.ps1
# 2. real subagent — MUST write one line, accents intact
'{"hook_event_name":"SubagentStop","agent_type":"Explore","last_assistant_message":"Revisión: sección lista"}' |
  powershell -NoProfile -ExecutionPolicy Bypass -File .claude\hooks\subagent-capture.ps1
(Get-Content docs\context\results.md).Count - $before   # expect exactly 1
```

Remove the test line afterwards. If case 1 writes anything, the gate is wrong — fix it before reporting the project as conforming.

Then report:
- created / kept / overwritten / merged, per file;
- where each skill was satisfied (global / project copy / installed now);
- the persona used (default or custom one-liner);
- prefill counts if Step 4 ran;
- a reminder that the hooks are live from the next turn/session events and `/compact-context` is available.
