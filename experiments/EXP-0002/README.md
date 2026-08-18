# EXP-0002 — Bidirectional Symbol–Feature Localization

Run from repository root:

```bash
python scripts/run_exp0002.py
```

Primary outputs:

- `results/metrics.json` — aggregate three-seed measurements and hypothesis decisions;
- `results/per_seed.jsonl` — full stage-wise hidden vectors, feature scores and round-trip records;
- `results/report.md` — human-readable interpretation;
- `3m/` — bounded 3M matrix-ledger projection;
- `corpus/train.jsonl` — complete finite training corpus;
- `features/feature_catalog.json` — explicit feature catalog.

This is a transparent toy-model mechanism experiment, not a proprietary-LLM hidden-state measurement.
