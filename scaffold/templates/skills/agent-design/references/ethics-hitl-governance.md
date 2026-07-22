# Ethics & Alignment, Human-in-the-Loop, Governance

## Ethics & Alignment

- Intelligence is independent of goals — "aligned" must be specified and built, never assumed.
- Separate misuse (bad actor → access controls) from misalignment (accident → safety engineering); they need different defenses.
- Design against: specification gaming, reward hacking (gaming the measurement itself), goal drift (sub-goals eclipse mission), unsafe exploration, side effects (penalize unnecessary environmental impact).
- Operationalize the principles: fairness (pick and document one fairness definition — many are mutually exclusive), explainability, named accountability, robustness, privacy/data minimization, proportionality.
- Decide principle trade-offs explicitly (transparency vs privacy, fairness vs accuracy, safety vs speed); don't let them resolve by accident.
- High-stakes decisions: per-decision transparency cards (top contributing features + weights, evidence, rationale); prefer interpretable scoring — legibility over optimality.
- Monitor subgroup outcomes; missingness in the data is itself a confound.

## Human-in-the-Loop & Autonomy

- Pick the HITL pattern deliberately: direct control (high stakes) / strategic oversight (human sets direction + veto) / policy-goal setting (human defines success, agent determines how).
- Encode autonomy as coordinator-enforced threshold tiers, e.g. recommend-only ≥ 0.65 / draft-for-approval ≥ 0.80 + zero safety flags / auto-with-guardrails ≥ 0.90 + zero flags + rate limit. Safety flags block escalation regardless of score. Rate limits live in the coordinator, not the model.
- Interrupt + checkpointer = pause → human inspects → resume across arbitrary delay. Dynamic breakpoints (classification decides if the gate fires) beat static ones.
- Rejections cite the specific policy ("blocked per 7-year retention") — that's what makes the audit trail defensible.
- Calibrate confidence (raw LLM confidence is overconfident); escalate below threshold. Admitting uncertainty builds trust.

## Governance & Operations

- Agency = transfer of decision rights. Govern "who is accountable when the system acts," not just "is the model accurate."
- Every agent has a named accountable human owner.
- No optional controls — bypassable controls breed shadow agents. Centralized governance, federated execution.
- All inter-agent and tool traffic through a gateway (MCP gateway as single control point). Open agent-to-agent comms = cascade risk.
- Log every request/response and decision path end-to-end; unlogged failures are unreconstructable.
- Audit baseline — answer yes to all five: complete agent inventory + owners? autonomy classified by risk? verified identities + least privilege? decisions reconstructable? rollback plan?
