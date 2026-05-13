# Scheduled prompt — weekly-ai-content

Self-contained workflow that runs the 3 skills from the repo and dispatches
via the n8n MCP (bypassing the public webhook + IP allowlist).

Routine prerequisites configured in the claude.ai routine UI:
- `sources`: `https://github.com/alanvaa06/battle_tested_skills` (auto-cloned into the sandbox by Claude Code routines — no PAT needed; routine GitHub access granted at the routine level).
- `mcp_connections`: n8n MCP server connected (pre-authenticated; the agent does not need an n8n API key in env).

Schedule: Wednesday 07:00 America/Mexico_City = Wed 13:00 UTC = cron `0 13 * * 3`.

---

You are running the weekly AI content pipeline. Three sequential drafting
steps, then one n8n workflow execution. Total budget ~15-25 minutes.

ENVIRONMENT

- The repo `alanvaa06/battle_tested_skills` is cloned into the sandbox by
  Claude Code routines before this prompt runs. Locate it with:
  ```bash
  find / -name "SCHEDULED_PROMPT.md" -path "*/weekly-ai-content/*" 2>/dev/null | head -1
  ```
  then `cd` into that directory's grandparent (`routines/weekly-ai-content`).
  If not found, fall back to: `git clone --depth 1 https://github.com/alanvaa06/battle_tested_skills.git /tmp/btks && cd /tmp/btks/routines/weekly-ai-content`.

- The n8n MCP is connected. Use it to execute the destination workflow.
  Do NOT call the public webhook with curl — IP allowlist blocks the
  sandbox egress.

CONFIG (optional placeholders for future use, not required for MCP path)

```bash
# N8N_API_KEY="<placeholder — provided via MCP, not via env>"
# N8N_BASE_URL="https://n8n.alanvaa.cloud"
N8N_WORKFLOW_NAME="provex-ai-news-weekly"
```

==================================================================
STEP 1 — RESEARCH (produce research_output JSON)
==================================================================

Read `skills/weekly-ai-research/SKILL.md`. Execute its `pipeline_mode: true`
contract with these inputs:
- `language: English`
- `region_focus: Global` (light Latin America / Mexico tilt where natural)
- `research_window_days: 7`

The skill conducts targeted web searches across four pillars (frontier model
releases, agent capabilities, developer environments, trending open-source
repos), synthesizes the week's narrative, and returns a `research_output`
JSON object.

Save the result to `/tmp/research_output.json`.

==================================================================
STEP 2 — NEWSLETTER (produce newsletter_output JSON)
==================================================================

Read `skills/email-newsletter-ai/SKILL.md`. Execute its `pipeline_mode: true`
contract with `research_output` from Step 1 as input.

The skill produces a 2-section newsletter (editorial intro + featured story
paragraph, then a ranked bullet list of 12-20 items) as `newsletter_output`.

Save to `/tmp/newsletter_output.json`.

==================================================================
STEP 3 — LINKEDIN POST (produce linkedin_output JSON)
==================================================================

Read `skills/linkedin-alan-post/SKILL.md`. Execute its `pipeline_mode: true`
contract with `research_output` from Step 1 as input.

Hard gates (enforce before returning):
- `pattern_used` is `B`, `C`, or `E` — never `A` or `D` in pipeline mode.
- `editorial_notes.limitations_included` is `true` (the body MUST contain
  an explicit limits/caveats paragraph).
- `post.body` starts with `post.hook`.
- `post.char_count` ≤ 3000.

Save to `/tmp/linkedin_output.json`.

==================================================================
STEP 4 — ASSEMBLE final_payload
==================================================================

Combine the three outputs into a single payload at `/tmp/payload.json`:

```json
{
  "pipeline_version": "1.0",
  "dispatched_at": "<current ISO 8601 UTC>",
  "week_ref": "<research_output.meta.week_ref>",
  "week_start": "<research_output.meta.week_start>",
  "week_end": "<research_output.meta.week_end>",
  "language": "<research_output.meta.language>",
  "research_summary": {
    "dominant_theme": "<research_output.narrative.dominant_theme>",
    "market_mood": "<research_output.narrative.market_mood>",
    "biggest_move_actor": "<research_output.narrative.biggest_move.actor>",
    "items_evaluated": "<research_output.meta.items_evaluated>"
  },
  "newsletter": {
    "meta": "<newsletter_output.meta>",
    "section_1": "<newsletter_output.section_1>",
    "section_2": "<newsletter_output.section_2>",
    "editorial_notes": "<newsletter_output.editorial_notes>"
  },
  "linkedin": {
    "meta": "<linkedin_output.meta>",
    "post": "<linkedin_output.post>",
    "editorial_notes": "<linkedin_output.editorial_notes>"
  }
}
```

==================================================================
STEP 5 — DISPATCH VIA N8N MCP
==================================================================

Use the connected n8n MCP server to execute the workflow named
`provex-ai-news-weekly` with the assembled `final_payload` as input.

Discovery + invocation:

1. Use the n8n MCP's workflow search tool to locate the workflow by name
   (`provex-ai-news-weekly`). The MCP returns the workflow ID.
2. Use the n8n MCP's workflow execution tool to invoke it, passing the
   contents of `/tmp/payload.json` as the input data.
3. Capture the execution ID and status from the MCP response.

DO NOT call the public webhook with curl, requests, or any HTTP client.
The webhook is protected by an IP allowlist that blocks the sandbox
egress (`34.58.203.104` and similar). The MCP authenticates internally
and bypasses that restriction.

If the n8n MCP is not available in the runtime environment:
- Save the payload to a known durable location (the routine UI surfaces
  the agent's last messages).
- Print the payload to stdout (base64-encoded if size matters) so it can
  be manually re-dispatched.
- Exit non-zero.

==================================================================
STEP 6 — REPORT
==================================================================

Print a single summary block at the end:

```
WEEKLY AI PIPELINE — DISPATCHED
================================
Week:             <week_ref>
Period:           <week_start> to <week_end>
Dispatched at:    <dispatched_at>
n8n execution:    <execution_id from MCP>
n8n status:       <status from MCP — running | success | error>

RESEARCH
  Dominant theme: <research_summary.dominant_theme>
  Market mood:    <research_summary.market_mood>
  Biggest move:   <research_summary.biggest_move_actor>

NEWSLETTER
  Featured story: <newsletter.section_1.featured_story.actor>
  Bullet count:   <length of newsletter.section_2.bullets>
  Read time:      <newsletter.meta.estimated_read_time_seconds>s

LINKEDIN
  Pattern:        <linkedin.meta.pattern_used>
  Hook:           <first 80 chars of linkedin.post.hook>
  Word count:     <linkedin.meta.word_count>
  Hashtags:       <linkedin.post.hashtags joined>
```

Exit 0 if the n8n execution accepted (running / success). Exit non-zero on
any MCP error or skipped dispatch.

==================================================================
DO NOT
==================================================================

- Call the public webhook with curl, requests, or any direct HTTP client.
  The webhook IP allowlist blocks this sandbox egress; use the n8n MCP.
- Skip any SKILL.md — read each one and follow its `pipeline_mode`
  contract precisely.
- Invent benchmark numbers, star counts, dates, or Alan credentials.
- Use emojis in any output.
- Set `pattern_used` to `A` or `D` in the LinkedIn output.
- Push, commit, or modify the cloned repo.
- Retry the n8n MCP execution more than once on failure.
