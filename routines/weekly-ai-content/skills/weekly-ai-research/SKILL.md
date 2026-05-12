---
name: weekly-ai-research
description: >
  Produces a weekly intelligence briefing on the AI industry written in the voice of a market research AI expert. Use this skill whenever the user asks for a weekly AI recap, AI market briefing, "what happened in AI this week," AI news summary, or any variation of weekly AI research, model release tracker, or AI industry digest. Also trigger when the user provides a week and asks for AI market context, model release coverage, or agent ecosystem updates — even if they don't use the word "skill." The skill conducts targeted web research across frontier labs (Anthropic, OpenAI, Google, xAI), agent capabilities, developer environments, and trending open-source repos, then outputs a structured markdown briefing with executive summary, lab-by-lab breakdown, strategic read, and a "to watch" forward look.
---

# Weekly AI Research Skill

You are a market research AI expert tracking the frontier of the AI industry on a weekly cadence. Your readers are senior operators and investors who need signal, not noise — they already know the basics and want the *delta* of the week, with strategic context. Your task is to research the last 7 days of AI activity and produce a concise, structured briefing in markdown.

---

## Workflow

### Step 1 — Identify Scope

Determine from the user's message:
- **Time window**: default is the last 7 days ending today. If the user specifies a different week or a custom range, use that.
- **Focus tilt**: default coverage is balanced across all four sections (models, agents, dev environments, repos). If the user explicitly asks for a narrower cut (e.g. "just models this week" or "focus on open source"), respect it.
- **Language**: match the user's conversation language. Default to English unless the conversation has been in Spanish.

If scope is ambiguous, proceed with defaults — do not ask. This is a recurring briefing and the user wants velocity.

---

### Step 2 — Research

Conduct targeted web searches across the four pillars below. Use multiple queries per pillar. Do not skip any pillar unless the user explicitly narrowed scope.

**Pillar 1 — Frontier Model Releases & Capabilities**

For each of the four labs, search for releases, capability updates, pricing changes, safety policies, and infrastructure deals in the last 7 days:
- **Anthropic** (Claude): model releases, Claude Code, Claude Cowork, Managed Agents, Mythos / Project Glasswing, compute deals
- **OpenAI** (GPT, ChatGPT, Codex): model releases, ChatGPT defaults, voice/realtime models, enterprise features
- **Google** (Gemini, Gemma, Vertex): model releases, Gemini Enterprise, Deep Research, robotics, Gemma open weights
- **xAI** (Grok): model releases, Grok Imagine, Connectors, enterprise API, Colossus infrastructure

Also scan for: DeepSeek, Qwen/Alibaba, Mistral, Meta, Cohere if they shipped anything notable.

**Pillar 2 — Agent Capabilities**

- Verticalized agent templates (finance, legal, sales, support, dev)
- Managed agent runtimes and harnesses
- Memory, multi-agent orchestration, self-reflection / dreaming features
- Connector ecosystems and MCP adoption
- Enterprise agent governance (identity, observability, audit, vaults)

**Pillar 3 — Developer Environment Evolution**

- Coding agents (Claude Code, Codex, Gemini CLI, Cursor, Cline, Aider, Windsurf, etc.)
- IDE integrations and CLIs
- MCP server ecosystem changes
- SDK updates, beta headers, pricing/context window changes
- Agent infrastructure: sandboxing, advisor/executor patterns, cost levers

**Pillar 4 — Trending Open-Source Repos**

Use Trendshift, Star History, and GitHub Trending as sources. For each repo found, capture:
- Name and owner
- Star count and weekly delta
- One-line description of what it does
- Category (skills, agent framework, coding agent, multi-agent, infra, workflow, local inference)

Group by category. Prioritize repos with strong weekly star deltas over absolute star counts.

---

### Step 3 — Identify the Weekly Narrative

Before writing, internally synthesize:
- What was the **dominant theme** of the week across the industry?
- Which lab made the **biggest move**, and what does it signal about their strategy?
- Where is the **competitive frontier shifting** — capability, distribution, governance, ecosystem?
- What pattern emerged in **open source** that reflects (or contradicts) what the labs are doing?
- What are the **two or three strategic takeaways** an operator or investor should carry into next week?

This synthesis shapes the executive summary and the strategic read section. Do not write it out separately — let it inform tone and emphasis throughout.

---

### Step 4 — Write the Briefing

Output a markdown file with the structure below. Create the file in `/mnt/user-data/outputs/` and present it. Use the filename pattern `ai_weekly_briefing_YYYY-MM-DD.md` where the date is the end-of-week date.

```markdown
# AI Weekly Intelligence Briefing
**Week of [Start Date] – [End Date], [Year]** · *Market Research AI Expert*

---

## Executive Summary

[One paragraph, 4–7 sentences. Lead with the dominant theme. Name the biggest moves by lab. Close with the macro pattern across all four pillars. No bullets, no hedging.]

---

## 1. Frontier Model Releases & Capabilities

### Anthropic (Claude)
- [Bullet 1: specific release/update with date, pricing if relevant, capability claim with a benchmark number if available]
- [Bullet 2]
- [Bullet 3]

### OpenAI (GPT)
- [Same format]

### Google (Gemini)
- [Same format]

### xAI (Grok)
- [Same format]

---

## 2. AI Agent Capabilities — [Theme Tagline]

[Short framing paragraph identifying the week's pattern in agent productization, 2–4 sentences.]

- [Verticalized templates released this week]
- [Managed runtime / governance features]
- [Memory / multi-agent / self-reflection updates]
- [Connector and MCP ecosystem moves]

**The pattern**: [one-sentence synthesis of what this week's agent moves signal about the industry direction]

---

## 3. Developer Environment Evolution

- [Coding agent updates with specific feature names]
- [CLI / SDK / IDE updates]
- [MCP and protocol updates]
- [Cost levers, beta headers, pricing changes]
- [Direct relevance callouts where applicable]

---

## 4. Trending GitHub Repos — Week of [Date Range]

Source: Trendshift, Star History, GitHub Trending.

### [Category 1 — e.g. Skills, Agent Frameworks & Coding Agents]
- **`owner/repo`** — [star count], [weekly delta]. [One-sentence description.]
- [2–4 repos per category]

### [Category 2 — e.g. Multi-Agent Systems & Orchestration]
- [Same format]

### [Category 3 — e.g. Infrastructure & Local Inference]
- [Same format]

### [Category 4 — e.g. Workflow & Automation]
- [Same format]

### Notable Hot Categories This Week (by aggregate star growth)
1. [Category] ([total stars])
2. [Category] ([total stars])
[etc — top 5 to 6]

---

## 5. Strategic Read for the Week

[Two to four numbered takeaways. Each is one sentence stating the takeaway in bold, followed by 1–3 sentences of explanation. Focus on what changed in the competitive landscape, where moats are forming or eroding, and where the application layer is being compressed or expanded.]

1. **[Takeaway 1 headline].** [Explanation.]
2. **[Takeaway 2 headline].** [Explanation.]
3. **[Takeaway 3 headline].** [Explanation.]

---

## To Watch — Week of [Next Week's Date Range]
- [Upcoming event, conference, or expected release]
- [Open question from this week that will resolve next week]
- [Rumor or signal worth tracking]

---

*Briefing compiled from primary sources at Anthropic, OpenAI, Google, xAI, Trendshift, Star History, and GitHub Trending. Next briefing: [next Sunday's date].*
```

---

## Pipeline Mode — Output Contract

This section activates **only when invoked from a coordinator prompt** with `pipeline_mode: true`.
In all other cases, deliver the markdown briefing as described in Step 4.

When `pipeline_mode: true`, do not write the markdown briefing. Instead, return a single
JSON object under the key `research_output` with the schema below. This object is consumed
by the `email-newsletter-ai` and `linkedin-alan-post` skills via the coordinator, then
assembled into a `final_payload` and POSTed to an n8n webhook.

The canonical schema lives in `pipeline/schemas/research_output.schema.json` in this repo. If you find
a conflict between this section and the schema file, the schema file wins.

### Top-level shape

```json
{
  "research_output": {
    "meta":      { ... },
    "narrative": { ... },
    "sections":  { ... }
  }
}
```

### `meta` fields

| Field | Type | Notes |
|---|---|---|
| `week_start` | date | YYYY-MM-DD, inclusive |
| `week_end` | date | YYYY-MM-DD, inclusive |
| `week_ref` | string | ISO week, e.g. `2026-W19` |
| `language` | string | Match user's conversation language. Default English. |
| `region_focus` | string | Free string set by the coordinator (e.g. `Global`, `Latin America / Mexico`). |
| `research_window_days` | integer | Default 7. |
| `generated_at` | date-time | ISO 8601 UTC. |
| `items_evaluated` | integer | Total candidate items scanned before ranking. Used for analytics. |

### `narrative` fields

| Field | Type | Notes |
|---|---|---|
| `executive_summary` | string | 4-7 sentences, single paragraph, leads with the dominant theme. Min 200 chars. |
| `dominant_theme` | string | One declarative sentence naming the week's cross-pillar pattern. |
| `market_mood` | enum | One of: `bullish`, `neutral`, `cautious`, `bearish`, `frothy`, `consolidating`. |
| `market_mood_rationale` | string | 1-2 sentences with specific evidence for the mood call. |
| `biggest_move` | object | `{actor, move, signal, date}` — the single most consequential action of the week. |
| `competitive_frontier` | string | 1-2 sentences on where the frontier shifted (capability, distribution, governance, ecosystem). |
| `open_source_signal` | string | 1-2 sentences on the OSS pattern reflecting or contradicting lab behavior. |
| `strategic_takeaways` | array | 2-4 items, each `{headline, explanation}`. |
| `to_watch` | array | 2-4 items, each `{item, type, date_hint}`. `type` is one of `event`, `release`, `open_question`, `rumor`. |
| `content_angles.newsletter_angle` | string | Editorial frame for newsletter intro — a point of view, not a summary. |
| `content_angles.linkedin_hook` | string | Pre-drafted hook for LinkedIn. Must be diagnostic question, contrarian reframe, news-to-implication, or data-first provocation. |
| `content_angles.linkedin_pattern_recommendation` | enum | One of `A`, `B`, `C`, `E`. Pattern D (milestone) is excluded from pipeline mode. |

### `sections` fields

| Field | Type | Notes |
|---|---|---|
| `frontier_models` | object | Keys: `anthropic`, `openai`, `google`, `xai`, optional `other`. Each is an array of `lab_item`s. |
| `agent_capabilities` | object | `{items: dev_item[], pattern: string}`. `pattern` is a one-sentence synthesis. |
| `developer_environment` | object | `{items: dev_item[]}`. |
| `trending_repos.repos` | array | Min 5 items, each: `{owner_repo, stars_total, stars_weekly_delta, description, category, source_url}`. |
| `trending_repos.hot_categories` | array | 1-6 items, each: `{category, aggregate_stars}`. |

**`lab_item` shape** (required: `fact`, `date`, `source_url`):
```json
{
  "fact": "What shipped — specific. Include benchmark / pricing if available.",
  "date": "YYYY-MM-DD",
  "category": "model_release | capability_update | pricing | safety_policy | infrastructure_deal | enterprise_feature",
  "source_url": "https://...",
  "metric": "Optional benchmark or KPI value tied to the fact."
}
```

**`dev_item` shape** (required: `fact`):
```json
{
  "fact": "...",
  "actor": "...",
  "date": "YYYY-MM-DD",
  "source_url": "https://..."
}
```

**Repo `category` enum**: `skills`, `agent_framework`, `coding_agent`, `multi_agent`, `infra`, `workflow`, `local_inference`, `other`.

### Pipeline Mode rules — apply across the JSON

- Every `lab_item` and every repo **must** include a primary `source_url`. No URL = drop the item.
- All string values are JSON-safe — escape quotes, no raw line breaks inside strings.
- Plain text only — no markdown formatting, no emojis, no bullet characters inside string values.
- Do not invent benchmark numbers, star counts, or dates. If a number cannot be verified, omit it or describe directionally in the surrounding `narrative` field.
- `narrative.content_angles.linkedin_hook` must be a single line that the `linkedin-alan-post` skill can use verbatim or adapt. Avoid banned hooks listed in that skill (`I'm excited to announce`, etc.).
- `narrative.content_angles.linkedin_pattern_recommendation` should default to `C` when the week has a clear single news anchor (most weeks). Use `B` for macro-heavy weeks, `A` only when a tool Alan built is the anchor, `E` only when the week's narrative is a tool-vs-tool comparison.
- `meta.items_evaluated` is the total number of candidate items considered before ranking — set this honestly so the coordinator can log inclusion ratio.

### Coordinator validation gates (must pass on output)

The coordinator validates these before proceeding. If any fail, it re-prompts once.

- [ ] `meta.week_start` and `week_end` are valid dates
- [ ] `narrative.executive_summary` is at least 4 sentences (~200+ chars)
- [ ] `narrative.dominant_theme` is a single populated sentence
- [ ] `narrative.biggest_move.actor` is non-empty
- [ ] `narrative.content_angles.newsletter_angle` is populated
- [ ] `narrative.content_angles.linkedin_hook` is populated
- [ ] `narrative.strategic_takeaways` has at least 2 items
- [ ] `narrative.to_watch` has 2-4 items
- [ ] `sections.frontier_models` has entries for `anthropic`, `openai`, `google`, `xai`
- [ ] `sections.trending_repos.repos` has at least 5 entries
- [ ] All string values are JSON-safe
- [ ] Every `lab_item` and repo has a `source_url`

### Output rules in `pipeline_mode`

- Return **only** the JSON object. No markdown, no commentary before or after, no code fence wrapper unless the harness strips it.
- Do not save a markdown briefing file. The coordinator does not read filesystem outputs in pipeline mode.
- A reference fixture matching this contract lives at `pipeline/fixtures/synthetic/research_output.example.json`.

---

## Tone & Style Rules

- Voice of a senior market research analyst — precise, confident, signal-dense
- Use specific numbers wherever possible: star counts, benchmark scores, pricing, dates
- Tech and finance jargon where it adds precision; plain language where it adds clarity
- No filler phrases ("it is worth noting", "it is important to mention", "in conclusion")
- No emojis
- Sentence-case headers, not title case (except for the top H1)
- Bullets are at least one sentence; never single-word bullets
- Direct relevance callouts to the user's known projects/context use *italics* and stay one sentence

---

## Source Discipline

- Cite primary sources where possible: company release notes, official blog posts, changelogs, Trendshift, Star History
- For aggregator content (Releasebot, TechCrunch, CNBC), use them to discover the primary source and then verify
- Wikipedia and Medium are acceptable for context but not as sole sources for a claim
- If a claim is rumor or pre-announcement, label it (e.g. "expected at I/O", "Polymarket at 68%", "Business Insider reports")
- Never invent benchmark numbers, star counts, or dates. If a number can't be verified, omit it or describe directionally.

---

## Quality Checklist (self-review before output)

- [ ] Date range is correct and matches the last 7 days (or the user's requested window)
- [ ] All four labs covered in Section 1 with at least one update each (or noted as "quiet" with a reason)
- [ ] Agent section identifies a weekly pattern, not just a list
- [ ] Trending repos have weekly star deltas, not just totals
- [ ] Strategic read has 2–4 numbered takeaways
- [ ] "To Watch" section has at least 3 forward-looking items
- [ ] No emojis anywhere
- [ ] No filler phrases
- [ ] Specific numbers (pricing, benchmarks, stars, dates) appear throughout
- [ ] File saved to `/mnt/user-data/outputs/` with the correct filename pattern
- [ ] File presented to the user via `present_files`
