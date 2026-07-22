# Pre-Deployment Checklist

- [ ] PEAS table filled; performance measure checked for Goodhart effects
- [ ] Environment classified → architecture justified
- [ ] Input validation: toxicity, injection classifier, PII redaction
- [ ] Untrusted content never in system/developer prompts; tagged and role-isolated
- [ ] Extraction agents tool-less; structured outputs between nodes
- [ ] No auto-rendered external URLs; output sanitized
- [ ] Step limits + tool-call caps
- [ ] OS-level sandbox: egress allowlist, workspace-only writes, config files locked, approvals never cached
- [ ] Action tiers defined (auto / gate / block); HITL on irreversible actions
- [ ] Always-on context lean (<1,500 tokens); map-not-manual docs; compaction/clearing/memory lever chosen
- [ ] Full audit trail: every tool call, decision, approval, rejection — with rationale
- [ ] Tracing per OTel GenAI conventions (or `_meta` subset); content capture off by default; all error traces kept
- [ ] Named human owner; rollback plan
- [ ] Schema validation fail-fast on every output; prompts and schemas versioned
- [ ] Golden eval set incl. injection cases; calibration measured
- [ ] Subgroup fairness monitoring where decisions touch people
- [ ] ~40% post-launch optimization budget allocated
