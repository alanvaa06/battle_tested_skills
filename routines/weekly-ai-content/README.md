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
Read SCHEDULED_PROMPT.md and execute it.
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
| `SCHEDULED_PROMPT.md` | Entry point — paste into routine UI |
| `skills/weekly-ai-research/` | Step 1: research |
| `skills/email-newsletter-ai/` | Step 2a: newsletter writer |
| `skills/linkedin-alan-post/` | Step 2b: LinkedIn writer |

## Running manually

The routine runs end-to-end in the Claude Code scheduled remote agent.
Manual local testing is not part of this simplified setup.

## Schedule

Friday 07:00 America/Mexico_City. Scheduled remote agent invocation
(configured outside this repo).
