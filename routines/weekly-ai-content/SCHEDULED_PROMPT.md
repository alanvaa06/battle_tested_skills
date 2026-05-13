# Scheduled prompt — weekly-ai-content

Paste this verbatim into the scheduled remote agent (Claude Code routine,
`schedule` skill, or external cron firing `claude --prompt-file`). It
clones the repo, installs deps, and executes `coordinator.md` end-to-end.

Schedule: Friday 07:00 America/Mexico_City.

---

You are the runner for the weekly-ai-content routine.

ENVIRONMENT

Set these at the top of the run (private repo — URL is intentionally
committed; rotate only if compromised):

```bash
export WEEKLY_AI_WEBHOOK_URL="https://n8n.alanvaa.cloud/webhook/provex-ai-news-weekly"
export WEEKLY_AI_LANGUAGE="${WEEKLY_AI_LANGUAGE:-English}"
export WEEKLY_AI_REGION_FOCUS="${WEEKLY_AI_REGION_FOCUS:-Global}"
export WEEKLY_AI_ARCHIVE_DIR="${WEEKLY_AI_ARCHIVE_DIR:-$HOME/ai-pipeline-archive}"
```

Verify `WEEKLY_AI_WEBHOOK_URL` is non-empty before continuing. If empty,
abort and report.

SETUP

1. Clone the repo (private, requires auth in the sandbox):
   ```bash
   git clone --depth 1 https://github.com/alanvaa06/battle_tested_skills /tmp/btks
   ```
2. Move into the repo root:
   ```bash
   cd /tmp/btks
   ```
3. Install Python deps:
   ```bash
   pip install -q jsonschema referencing requests
   ```
4. Verify the `tools/*` helpers import cleanly:
   ```bash
   python -c "from tools.assemble_payload import assemble_final_payload; from tools.validate_payload import validate; from tools.post_to_n8n import post_payload; print('tools ok')"
   ```

EXECUTE

1. Move into the routine:
   ```bash
   cd /tmp/btks/routines/weekly-ai-content
   ```
2. Read `coordinator.md`.
3. Follow every step in `coordinator.md` exactly, in order. Use the
   `tools/*` helpers as the coordinator instructs. Do not skip validation
   gates.
4. The coordinator handles: invoking the 3 skills (weekly-ai-research,
   email-newsletter-ai, linkedin-alan-post), validating each output
   against its schema, assembling `final_payload`, POSTing to
   `$WEEKLY_AI_WEBHOOK_URL` with retries, and archiving to
   `$WEEKLY_AI_ARCHIVE_DIR/<week_ref>.json`.

ON SUCCESS

- Print the Step 5 terminal report from `coordinator.md`.
- Exit 0.

ON FAILURE

- If any skill validation fails twice, abort and save the error JSON to
  `$WEEKLY_AI_ARCHIVE_DIR/<week_ref>-error.json`.
- If the webhook POST fails after the single retry, leave the payload
  archived and exit non-zero.
- Print HTTP code, response body, and which step failed.

DO NOT

- Edit `coordinator.md` or any skill `SKILL.md` mid-run.
- Push, commit, or modify the cloned repo.
- Skip the validation gates even if the schema "looks right" by inspection.
