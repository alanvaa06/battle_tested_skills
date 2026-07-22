# Security

## Prompt injection — assume residual risk

Not solved (~1% attack success on best models = 1 in 100 documents at scale). Indirect injection via ingested content is the main threat. Layer all of:

1. Instruction hierarchy: untrusted content never enters system/developer prompts; wrap in `<untrusted>` tags routed through user/tool roles
2. Input classifiers on untrusted content
3. Output sanitization: strip external image URLs and suspicious links (0-click exfiltration class)
4. Action gating: human confirmation on sensitive actions — the last line
5. Least privilege + sandboxed execution
6. Injection test cases in the eval suite; rerun per model version

Architectural rules:
- **Extraction agents get no tools.** The agent reading untrusted content emits structured output only; tool-bearing agents consume that output, never raw text.
- **Storage-as-digest:** discard raw ingested content post-extraction — injection fires once, not on every retrieval.
- Narrow task scopes. "Handle my inbox" is a license to be hijacked; "reply to meeting requests only" is defensible.
- Never auto-render external URLs. Never run agent code without sandbox + approval. Never treat classifier passes as guarantees.

## Least privilege

- Grant the minimum tool/permission set. Narrow sets are also better-performing.
- Per-tool allowlists, scopes, budgets; per-agent rate limits; escalation runbooks with kill switches.
- Read access ≠ write access; SELECT ≠ INSERT. Scope credentials per capability.

## Sandboxing

- Enforce at OS level. App-layer controls lose subprocesses; attackers bypass allowlists via indirection through approved tools.
- Three mandatory controls:
  1. Network egress only to allowlisted destinations (blocks exfiltration, reverse shells)
  2. No file writes outside the workspace (blocks `~/.zshrc`-class persistence)
  3. No writes to agent config files ever — even in-workspace, even with approval. Hooks/MCP configs/skills execute outside the sandbox and are the escape vector. Manual human edit only.
- Sandbox boundary and approval policy are separate, composable controls: autonomy inside, approval at every crossing.
- **Never cache approvals.** Allow-once/run-many is not a control.
- Inject secrets per task via broker; never inherit host environment. Recycle sandboxes (ephemeral or scheduled rebuild).
- High-risk autonomy → virtualize the kernel (microVM/Kata/VM); Seatbelt/bubblewrap/Docker share the host kernel.

## Action classification

Three tiers, not binary:

| Tier | Action |
|---|---|
| Safe/read | Auto-execute |
| Reversible write, targeted | Human approval gate |
| Destructive/mass | Block outright — **before** the human gate; reviewer attention is the scarcest resource |

## Memory security

- Multi-pass secret scan before persistence: raw → zero-width strip → Unicode NFKC normalize. Keep a generic backstop pattern (PEM header) for what structured patterns miss.
- Redaction = rollback to predecessor state, not erase. Cross-check IDs against forgery.
- Input validation at the boundary: toxicity, PII redaction, injection scrub.
