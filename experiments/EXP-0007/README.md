# EXP-0007 — Adaptive Epistemic Admission / Learning When to Trust

EXP-0007 extends EXP-0006 from fixed admissibility quorums to a history-conditioned admission policy.

The benchmark compares:

- `Static-Q2`
- `Static-Q3`
- `Learned-Adaptive`
- `Oracle` (evaluation ceiling only)

`Learned-Adaptive` receives **one-event-delayed feedback**. The current event's genuine/pollution label is never passed into `decide()`. Each provenance root has a Beta reliability posterior; admission requires enough trust-weighted independent-origin support for the current risk, novelty and recent pollution level.

Primary files:

- `results/report.md`
- `results/metrics.json`
- `results/per_event_summary.jsonl`
- `results/trust_trajectory.jsonl`
- `ledger/admission_events.jsonl`
- `3m/`

This is a bounded synthetic online benchmark over the canonical EXP-0004 F01–F19 SCI package. It performs no neural retraining, no public AI Board write and no live CTCL call.
