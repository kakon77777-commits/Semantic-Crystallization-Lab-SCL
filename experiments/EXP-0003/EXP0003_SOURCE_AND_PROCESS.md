# EXP-0003 Source and Process Record

## Source lineage

EXP-0003 inherits the finite semantic object from EXP-0001 and the transparent neural checkpoint construction from EXP-0002. The three preserved theory papers and the EML-U reference package remain under `papers/source-original/` in the byte-complete release and are tracked by SHA-256.

## Process

1. Recreate EXP-0002 Stage 2 independently for each seed `11`, `23`, `37`.
2. Freeze encoder and feature prototypes.
3. Fork five arms from the same per-seed state.
4. Keep `qevra` and `tivak` occurrence counts matched in all trainable arms.
5. Use a shared memory bank containing seven semantic entries and two pointer entries; memory texts contain neither target lexeme name.
6. Route query hidden states to memory keys by cosine-softmax attention.
7. Evaluate eight held-out contexts per symbol.
8. Measure context feature-signature JS, thresholded-support Jaccard, target recall, centroid-target JS, cross-seed centroid JS, reverse retrieval, hidden-context cosine dispersion, raw memory mass, and category-size-normalized memory density.
9. In A4, repeat retrieval and embedding-only learning for exactly three cycles.
10. Export all results into the bounded 3M ledger and verify checksums.

## Preserved negative result

`H2_diverse_learning_beats_repetition` is false in this run. Diverse contextual training improves target fidelity but does not beat repetition-only on the aggregate pure-stability metrics. No post-hoc change to that preregistered decision is made.
