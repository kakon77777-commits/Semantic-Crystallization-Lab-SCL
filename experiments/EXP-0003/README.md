# EXP-0003 — Semantic Basin Stabilization

This experiment starts from the exact EXP-0002 Stage-2 state for each seed and compares five arms:

- `A0_baseline`: no additional exposure;
- `A1_repetition`: repeated same semantic/pointer use;
- `A2_diverse`: unseen compatible contexts, no external memory;
- `A3_memory_only`: frozen parameters plus attention-selected external memory;
- `A4_attentive_consolidation`: three recall → attention → update cycles.

Only the `qevra` and frequency-matched `tivak` embedding rows may change after the common EXP-0002 checkpoint. The encoder and learned feature prototypes remain frozen.

Primary outputs:

- `results/metrics.json` — aggregate multi-seed metrics and hypothesis decisions;
- `results/per_seed.jsonl` — full raw seed ledgers;
- `results/per_seed_summary.jsonl` — compact per-seed summary;
- `results/report.md` — human-readable interpretation;
- `3m/` — bounded 3M matrix-ledger projection;
- `github-audit/` — partitioned UTF-8 reconstruction of the largest raw ledgers for GitHub synchronization.

The primary H4 gate requires lower intrinsic context JS, higher support Jaccard, and non-worse centroid-to-target JS on at least two of three seeds.

This is not an infinite-limit or general-LLM result.
