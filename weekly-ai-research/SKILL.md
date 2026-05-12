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
