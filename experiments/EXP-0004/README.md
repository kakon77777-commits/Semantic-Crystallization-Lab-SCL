# EXP-0004 — Cross-Agent Symbolic Cognitive Imprint Transfer

Three independently initialized tiny Transformers (seeds 11/23/37) are treated as separate bounded agents. They never share model weights or raw hidden coordinates.

The experiment tests four gates:

1. independent SCI reconstruction;
2. single-donor portable SCI transfer;
3. append-only objection/correction plus coordinate-wise median merge;
4. shared correlated-contamination stress.

Cross-agent comparison occurs only on the declared F01–F19 feature coordinate. The generated `ledger/ai_board_sci.jsonl` is AI-Board-compatible in spirit (append-only proposal/objection/correction events) but is not posted to the public Board. Logical instant fields are CTCL-compatible sequence identifiers, not live CTCL-verified instants.

Run:

```bash
python scripts/run_exp0004.py
```
