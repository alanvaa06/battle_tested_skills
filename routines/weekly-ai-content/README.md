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
