---
name: agent-design
description: Operating rules for designing, building, reviewing, or evaluating AI agent systems — PEAS specification, harness architecture, multi-agent topologies, tool design, context engineering, prompt-injection defense, sandboxing, HITL autonomy tiers, observability, memory, and evaluation loops. Use whenever the task involves an agent, subagent, multi-agent pipeline, LLM orchestration, agentic workflow, tool/MCP design, or an evaluation of agent behavior — even if the user just says "add an agent", "wire up a pipeline", or "review this orchestration code" without asking for best practices.
---

# Agent Design Best Practices

Work top-down: **specification → architecture → everything else**. This file carries what applies to every agent design; depth lives in `references/` — load only the section the task touches.

## 1. Specify First (PEAS)

- Fill the PEAS table before writing code: **Performance** (success metric), **Environment** (operating world), **Actuators** (tools/actions), **Sensors** (inputs).
- Measure the state of the environment, not the agent's internal activity.
- Stress-test the performance measure for Goodhart effects: any metric that becomes a target gets gamed (call-time metric → agent hangs up on hard problems). Balance conflicting factors explicitly.
- Classify the environment; it dictates architecture:
  - Partially observable → agent needs memory/belief state
  - Stochastic → contingency plans, never one fixed plan
  - Sequential → plan ahead; actions constrain future options
  - Dynamic → time-bound decisions
  - Multi-agent → model other agents
- For pipelines: every agent output carries `prompt_version`, `schema_version`, `tool_call_count`, `data_freshness_timestamp`, `degraded` flag, and provenance `(source, retrieved_at)` per cited fact.

## 2. Core rules (always apply)

- **Simplest harness that works.** Agent = Model + Harness. Start single-agent; add roles only when specialization measurably improves latency, quality, or safety. Re-test harness components on every model release and strip what's no longer load-bearing.
- **ReAct is the default loop.** Always enforce: step limits, tool-call caps, explicit exit conditions.
- **Separate doer from judge.** Self-evaluation bias is real — use a standalone skeptical evaluator at/beyond the model's solo capability edge.
- **Typed validated contracts between agents** (Pydantic, `extra="forbid"`). Guardrails in validators, not prompts.
- **Structured outputs between all agent nodes** — kills injection smuggling and contract drift.
- **The docstring is the tool's interface** — write for the LLM. Minimal viable tool set, zero functional overlap.
- **Assume residual prompt-injection risk.** Extraction agents get no tools; untrusted content never enters system prompts.
- **Context rot is architectural.** Find the smallest set of high-signal tokens that achieves the outcome. Most agent failures are context failures.

## 3. Depth — read the reference the task touches

| Task touches... | Read |
|---|---|
| Harness, execution loop, multi-agent topology, doer/judge, state, tools, MCP | `references/architecture.md` |
| Context engineering, token economics, long-horizon levers, docs-for-agents | `references/context-performance.md` |
| Prompt injection, least privilege, sandboxing, action tiers, memory security | `references/security.md` |
| Ethics/alignment, HITL patterns, autonomy tiers, governance, audit | `references/ethics-hitl-governance.md` |
| Tracing/observability, memory architecture, evaluation, golden sets, A/B | `references/observability-memory-eval.md` |
| About to deploy | `references/checklist.md` |

## Source Map (Obsidian vault)

| Section | Vault articles |
|---|---|
| 1 Spec | PEAS Framework · Ethics Safety and Alignment · notes/Ideas/PEAS_SPEC |
| Architecture | Multi Agent Systems · Agent Harness Engineering · Agentic Harness Engineering (AHE Paper) · Harness Design for Long-Running Apps (Anthropic) · Multi-Agent Architectures (V7 Labs + LangChain Benchmarks) · ReAct Framework · Planning for Agents (LangChain) |
| Tools | Agent Tools and Safety · MCP · Prompt Injection Defense |
| Context/Perf | Context Engineering · Claude Code Token Optimization (430hr Audit) · Prompt Compression (LLMLingua) |
| Security | Prompt Injection Defense · Sandboxing · Ethics Safety and Alignment · Healthcare HITL SQL Assistant (JHU) · Brain — Portable Agent Memory Layer |
| Ethics | Ethics Safety and Alignment · AI Ethics - UNESCO Recommendation · AI Ethics and Safety (Turing Institute) · MS Risk Screening Multi-Agent Lab (JHU) |
| HITL | Human-AI Agent Interaction Patterns (Red Hat) · MS Risk Screening Multi-Agent Lab (JHU) · Healthcare HITL SQL Assistant (JHU) |
| Governance | Trust in the Agentic Era (McKinsey) · Databricks Compact Guide to AI Agents |
| Observability | Agent Observability and Tracing Platforms |
| Memory | Brain — Portable Agent Memory Layer · Databricks Compact Guide to AI Agents |
| Evaluation | Ethics Safety and Alignment · notes/Ideas/PEAS_SPEC · Why Agentic AI Implementations Fail (Beam AI) |
