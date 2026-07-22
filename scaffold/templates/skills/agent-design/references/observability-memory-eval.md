# Observability, Memory, Evaluation

## Observability & Tracing

- Agent failures live in multi-step causal chains — single-call monitoring misses them. Trace full sessions.
- Instrument against OpenTelemetry GenAI semantic conventions, not a vendor SDK — backend stays swappable. Span tree (`invoke_agent` → `chat <model>` → `execute_tool`) mirrors the decision graph; MCP conventions link agent-side and server-side tool traces under one trace_id.
- Content capture default-off; production mode = external storage + URL reference (independent IAM and retention).
- Tail-based sampling: keep 100% of error / slow / high-span-count traces; sample routine ones.
- Minimum viable hand-rolled version: per-run `_meta` block (run_id, latency, tokens, tool calls with ok/error, degraded flag) on every agent output.
- Platform by bottleneck: OSS self-host → Langfuse; LangGraph → LangSmith; OTel-pure → Phoenix/OpenLLMetry; agent debugging → Laminar/AgentOps; eval CI gates → Braintrust; full-traffic eval → Galileo.

## Memory

- Memory portable, typed, indexed, audited — not a markdown blob plus an uninspectable vector store.
- Separate source of truth (append-only audited event log) from disposable rebuildable index.
- Type the memories: preference ≠ lesson ≠ claim — each needs different retrieval, visibility, and update rules. Typed memory = queryable memory.
- Under ~100K single-user events, weighted BM25 full-text matches embeddings with no model dependency. Don't default to vectors.
- Idempotency keys + retry loops the moment two writers can collide.
- Split short-term (working) from long-term (episodic) memory.

## Evaluation & Continuous Improvement

- Groundedness is the core trust metric: is every claim traceable to source evidence? Evaluate three stages: retrieval quality → faithfulness → answer quality.
- LLM-as-judge: judge stronger than the judged model, explicit rubrics, periodic validation against humans.
- Golden set: 10–15 frozen inputs + human-reviewed expected outputs + ground-truth labels. Regression baseline for everything.
- A/B prompt versions on the same golden set; promote only on positive primary-metric delta with zero guardrail regression.
- Weekly ritual: pull runs → score → diagnose by PEAS axis → patch ONE thing on ONE agent → A/B → promote → changelog. One change per cycle or deltas are unattributable.
- Never: prompt edit without version bump; promote on "feels better"; schema change without parallel-running both versions.
- Map the human process before building (the #1 failure cause is tech looking for a problem). Budget ~40% of project resources for post-launch optimization — launch is the start.
