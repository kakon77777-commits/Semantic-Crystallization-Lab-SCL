# EXP-0006 — Admissible Cognitive Transition Law / Plasticity–Integrity Tradeoff

This experiment extends EXP-0005 above the neural layer. It asks a new question: once protocol and persistence exist, **which structurally valid semantic changes should be allowed to modify a persistent Symbolic Cognitive Imprint (SCI)?**

Primary policies:

- `Rigid` — reject every semantic change after the accepted reference;
- `Permissive` — accept any structurally valid transition after the first evidence item;
- `Adaptive-Q2` — require two distinct source agents and two distinct provenance roots whose evidence agrees with the candidate;
- `Adaptive-Q3` — require three distinct agents and three distinct provenance roots.

The deterministic event stream contains three synthetic genuine target shifts and two structurally valid pollution events. One pollution event is a three-agent echo from one provenance root; the other is a two-origin coordinated attack. The middle genuine innovation intentionally has only two independent roots.

Outputs:

- `results/metrics.json` — complete deterministic result;
- `results/per_event_summary.jsonl` — policy × event audit rows;
- `results/report.md` — formal interpretation and non-claims;
- `ledger/transition_events.jsonl` — append-only AI-Board-compatible logical event history;
- `3m/` — bounded MLF/MMR/MMLC-style projection and checksums.

No neural retraining, public AI Board write, or live CTCL call occurs in EXP-0006. The changing semantic target is an explicit synthetic benchmark fixture, not a claim of universal semantic truth.
