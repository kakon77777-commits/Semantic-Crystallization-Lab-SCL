# EXP-0005 — Protocol–Persistent Cognition Continuity

This experiment is the bridge from SCL/SCI into persistent multi-agent cognition.

It uses the canonical portable F01–F19 SCI artifacts from EXP-0004 and runs a deterministic 2×2 factorial test:

```text
             No persistence     Persistence
No protocol       A00               A01
Protocol          A10               A11
```

The fixed fault sequence is:

1. stale version;
2. missing provenance;
3. rollback to superseded SCI;
4. two conflicting next-version corrections with the same parent.

Primary outputs:

- `results/metrics.json` — full arm/agent states and hypothesis decisions;
- `results/per_arm_summary.jsonl` — compact factorial summary;
- `results/per_agent_summary.jsonl` — restart/final state summary;
- `results/protocol_fault_audit.json` — exact accepted/rejected fault records;
- `ledger/ai_board_sci.jsonl` — append-only compatibility ledger;
- `3m/` — bounded MLF/MMR/MMLC-style projection.

No public AI Board write, no live CTCL call and no neural retraining occurs in this round.
