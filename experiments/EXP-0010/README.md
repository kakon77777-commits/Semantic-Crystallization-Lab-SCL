# EXP-0010 — Reflexive Epistemic Challenge / X-Order Cognitive Lift

This experiment tests whether prior SCL experiment artifacts can causally alter a later decision policy on **newly instantiated** fixtures, then asks whether a second-order self-model improves further once the environment is allowed to target the first-order meta-rule.

## Arms

- `A0-Reactive` — no artifact exposure; EXP-0009 reactive Belief-State baseline.
- `A1-Artifact-Reflexive` — reads a SHA-audited rule pack compiled from EXP-0001–0009 artifacts.
- `A2-Second-Order` — additionally models attacks against the A1 challenge rule.
- `Oracle` — evaluation ceiling only.

## Phases

1. `novel_transfer` — new homologous failure classes, exact-hash replay forbidden.
2. `meta_adversarial` — boundary-skimming / slow-roll / false-disagreement attacks conditioned on A1.

## Key bounded result

A1 sharply improves the novel-transfer phase (`0.14026 → 0.01647` loss) and catches a new high-confidence A0 error. A1 is then exploited by three Phase-II meta-attacks. A2 triggers one second-order challenge but catches none of those exploits and slightly increases meta-phase loss through added evidence cost.

So this run supports a bounded **0→1 reflexive lift** but does not support monotone `1→2` improvement.

Reproduce:

```bash
python scripts/run_exp0010.py
python -m pytest -q
npm test
```

See `results/report.md`, `EXP0010_SOURCE_AND_PROCESS.md`, and `3m/`.
