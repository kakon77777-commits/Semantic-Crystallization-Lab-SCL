# EXP-0012 — Autonomy Under Epistemic Pressure / Active Inquiry Resolution

This experiment asks whether the defer-heavy closed-loop safety of EXP-0011 can be converted into immediate autonomous epistemic resolution while holding the evidence budget fixed.

Primary outcome: the frozen A4 one-step value-of-information planner collapses into `defer` on all 20 events. That is a negative autonomy result, not a runner failure. The post-hoc sensitivity grid is stored separately and is explicitly exploratory.

Reproduce:

```bash
python scripts/run_exp0012.py
python -m pytest -q
npm test
```

See `results/report.md` for the interpretation and `3m/` for bounded 3M audit exports.
