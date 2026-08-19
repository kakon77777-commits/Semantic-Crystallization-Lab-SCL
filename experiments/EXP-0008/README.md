# EXP-0008 — Adaptive Trust Dynamics / Reputation Decay–Recovery

This experiment extends SCI admission from **learning whom to trust** to **how fast trust itself should change**.

It compares Cumulative-History, Fixed-Decay, Adaptive-Dynamics and an Oracle ceiling while holding the downstream admission formula fixed. The 20-event benchmark stresses source cold-start, rapid betrayal, rehabilitation and later provenance drift.

Reproduce:

```bash
python -m pytest -q
npm test
python scripts/run_exp0008.py
```

Primary report: `results/report.md`. Raw event/trust ledgers and bounded 3M projections are emitted beside it.
