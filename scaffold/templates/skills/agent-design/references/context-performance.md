# Context & Performance

## Context engineering

- Context rot is architectural: recall degrades as the window fills, in all models. Find the smallest set of high-signal tokens that achieves the outcome. Most agent failures are context failures.
- System prompt at the right altitude: between hardcoded if-else logic and vague guidance. Minimal ≠ short — minimal full specification.
- Few-shot: curated canonical examples, never edge-case laundry lists.
- Just-in-time retrieval: keep lightweight identifiers (paths, queries, links), load at runtime. Hybrid (stable context up front + runtime exploration) is the default.
- Three levers for long horizons — match to the observed growth problem:

  | Lever | When |
  |---|---|
  | Compaction (summarize transcript, reinit) | Long dialogue |
  | Tool-result clearing (drop re-fetchable payloads, keep call record) | Bulky tool results — safest lever |
  | Memory/notes (persist outside window) | Work spans sessions |

- Fourth lever: subagents with clean windows returning 1–2K-token distilled summaries.
- Docs for agents: map, not manual. ~100-line entry file pointing into structured versioned docs (progressive disclosure). One big instruction file crowds out the task, rots, and is unverifiable. Anything the agent can't reach in-context doesn't exist — keep knowledge in repo-local versioned artifacts.

## Token economics

- Audit always-loaded overhead first; it can hit 73% of spend. Target <1,500 tokens of always-on context; move repeated patterns into on-demand modules.
- History re-reads compound (message 30 costs 30× message 1) — cap conversation length, summarize and restart.
- Every always-on hook, MCP schema, and tool definition is a per-request tax. Disable what you can't justify.
- Extended thinking off by default; per-task only.
- Cheap model on bloated context costs more than expensive model on lean context. Fix overhead before downgrading models.
- Exploit prompt-cache TTLs; session resumes after TTL silently multiply cost.
- Track per run with hard targets: schema validity 100%, latency p95, tokens/run, tool-call avg, degraded rate, hallucination rate.
- QA/evaluator passes cost ~5% of generation and catch real gaps — budget them in.
