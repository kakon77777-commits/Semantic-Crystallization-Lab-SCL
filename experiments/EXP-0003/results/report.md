# SCL EXP-0003 — Semantic Basin Stabilization

## Boundary

This is a finite supervised proof-of-mechanism on the transparent tiny PyTorch Transformer from EXP-0002. It does not expose ChatGPT or proprietary-model hidden states and does not establish a universal semantic fixed point.

After recreating the exact EXP-0002 Stage-2 state for each seed, every trainable EXP-0003 arm freezes the encoder and feature prototypes. Only the `qevra` and frequency-matched `tivak` embedding rows may move.

## Primary stability result

For compatible contexts, lower mean pairwise JS means less feature-signature drift, while higher support Jaccard means more agreement of thresholded feature sets.

| Arm | qevra context JS | support Jaccard | target recall | centroid→target JS | cross-seed centroid JS |
|---|---:|---:|---:|---:|---:|
| A0_baseline | 0.0834 | 0.6291 | 0.6181 | 0.0526 | 0.0559 |
| A1_repetition | 0.0630 | 0.6975 | 0.6968 | 0.0414 | 0.0413 |
| A2_diverse | 0.0704 | 0.6678 | 0.6921 | 0.0342 | 0.0267 |
| A4_attentive_consolidation | 0.0588 | 0.7207 | 0.7106 | 0.0356 | 0.0329 |

### External-memory assistance

- A3_memory_only assisted: context JS=0.0248, support Jaccard=0.8254, target recall=0.8218, centroid-target JS=0.0250.
- A4_attentive_consolidation assisted: context JS=0.0119, support Jaccard=0.9190, target recall=0.8773, centroid-target JS=0.0216.

## Hypothesis decisions

- H1 baseline semantic-domain instability exists: **SUPPORTED**.
- H2 diverse learning beats repetition on stability: **NOT SUPPORTED**.
- H3 memory assists without intrinsic consolidation: **SUPPORTED** (3/3 seeds improve under assistance; intrinsic equality=True).
- H4 attentive recall-coupled consolidation stabilizes intrinsically: **SUPPORTED** (2/3 seeds satisfy the full preregistered directional gate).
- H5 attention routing aligns with semantic vs pointer memory after category-size normalization: **SUPPORTED** (3/3 seeds).

H2 is important: mere repetition can stabilize a small learned symbol as well as or better than diverse reuse under some metrics. Diversity may improve target fidelity without automatically producing the lowest context variance. Stability and semantic accuracy are therefore distinct axes.

## A4 cycle trajectory

| Cycle | qevra context JS | support Jaccard | target recall | qevra semantic density | tivak pointer density |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.0784 | 0.6241 | 0.6389 | 0.1310 | 0.2200 |
| 2 | 0.0687 | 0.6729 | 0.6736 | 0.1318 | 0.2194 |
| 3 | 0.0588 | 0.7207 | 0.7106 | 0.1323 | 0.2176 |

## Attention-mass caveat

The shared memory bank contains seven semantic entries and two pointer entries. Raw category mass is therefore reported but is count-biased. The routing hypothesis is judged using per-entry category density (category mass divided by category entry count) and top-ranked memory evidence, while raw mass remains in the ledger for audit.

## Interpretation

The bounded result supports the refined SCL view that a compact symbol can become a more stable address into a distributed semantic feature region through repeated attentive recall and learning. It does not require, and does not claim, that more meaning corresponds to more simultaneously active hidden coordinates.

Memory-only assistance is not the same as consolidation: A3 can improve the current inference by retrieving semantic structure while leaving the intrinsic symbol representation exactly unchanged. A4 tests whether repeated retrieval plus learning transfers part of that external support back into the symbol's intrinsic feature basin.

## Per-seed primary gate

- Seed 11: PARTIAL — JS 0.1350→0.1227; Jaccard 0.5322→0.5175; target JS 0.1042→0.0644.
- Seed 23: PASS — JS 0.0831→0.0329; Jaccard 0.5831→0.7950; target JS 0.0308→0.0251.
- Seed 37: PASS — JS 0.0320→0.0207; Jaccard 0.7719→0.8496; target JS 0.0228→0.0172.

## Non-claims

- no infinite-limit convergence claim;
- no claim that natural-language feature domains are fixed points;
- no claim that this external memory router equals production LLM attention or memory;
- no claim that reduced variance alone means richer semantics; target fidelity and pointer leakage are reported together;
- no ontological or cardinality theorem from the source papers is proven here.
