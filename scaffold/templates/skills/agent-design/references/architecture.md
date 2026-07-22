# Architecture, Tools & Interfaces

## Simplest harness that works

- Agent = Model + Harness. Harness primitives: filesystem (durable state, offload, collaboration surface), bash/code execution (agent builds its own tools), sandbox, verification tooling (tests, logs, browser) for self-verification loops.
- Start single-agent. Add roles only when specialization measurably improves latency, quality, or safety.
- Every harness component encodes an assumption about what the model can't do. On every new model release, re-test and strip components no longer load-bearing.
- The harness is a performance lever with the model held fixed (Terminal-Bench Top 30 → Top 5 on harness changes alone). Don't assume the model's native harness is optimal for your task. Invest harness effort in tools, middleware, and memory — evolving the system prompt alone regresses.

## Execution loop

- ReAct (Think → Act → Observe) is the default loop. Plan-and-Execute for complex sequential tasks where upfront reasoning prevents myopic errors. Rigid fixed plans only for unchanging workflows.
- Always enforce: step limits, tool-call caps, explicit exit conditions.
- Debug by reading the trace: wrong Think → fix system prompt; wrong Act → fix tool docstring; wrong Observe → fix tool implementation; loop → add limits.

## Multi-agent

- Hub-and-spoke topology; each agent talks to 1–2 others max. Coordination cost explodes past 2–3 agents.
- Swarm slightly outperforms Supervisor (sub-agents answering users directly avoids translation overhead). Single agent degrades sharply beyond 2 distractor domains.
- Design against the four MAS failure modes:
  - Deadlock → timeouts + coordinator oversight
  - Echo chambers → require citations + independent verification before consensus
  - Role collapse → strict role prompts with explicit forbidden actions
  - Hallucinated handoffs → ack/receipt messages with IDs; coordinator asserts on missing acks
- Build order: roles → tools (schemas + validation) → coordinator (turn-taking, budgets, stop conditions) → tracing → SLOs → eval loop.

## Separate doer from judge

- Self-evaluation bias is real: agents approve their own mediocre work. Use a standalone skeptical evaluator agent.
- 3-agent pattern for long autonomous work: planner (short prompt → spec, high-level only) + generator + evaluator (tests the live artifact, hard fail thresholds, detailed feedback).
- Negotiate "done" criteria between generator and evaluator before work starts.
- Calibrate the evaluator with few-shot scoring examples; out of the box it finds real issues then approves anyway.
- Evaluator only pays off at/beyond the model's solo capability edge; inside it, it's overhead.
- Counter context anxiety (premature wrap-up near window limits) with context resets: clear window + structured handoff.

## State & contracts

- Typed validated contracts between agents (Pydantic, `extra="forbid"`). Enforce guardrails in validators, not prompts (e.g., confidence ≤ 0.5 when inputs stale; downstream agents cannot mutate upstream deterministic verdicts).
- Checkpointer for any workflow with human delays; per-user thread IDs for state isolation.

## Tools & Interfaces

- The docstring is the interface — write for the LLM. Type hints mandatory. Return strings/JSON. Catch errors inside the tool and return them as observations.
- Minimal viable tool set, zero functional overlap. If a human can't say which tool applies, the agent can't.
- Guardrails as tools the agent must call (e.g., fairness check before decision), not prompt instructions.
- Use MCP for tool exposure: open standard, dynamic discovery, reusable servers.
- Structured outputs (schema-constrained JSON/enums) between all agent nodes — kills both injection smuggling and contract drift.
- Test robustness with deliberately failing tool variants.
