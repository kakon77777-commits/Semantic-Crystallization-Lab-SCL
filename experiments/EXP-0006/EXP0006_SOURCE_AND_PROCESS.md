# EXP-0006 Source and Process Record

## Input lineage

EXP-0006 consumes the canonical `merged_qevra` portable SCI package from EXP-0004 in the shared `SCL-F01-F19-v0.2` coordinate space. EXP-0005 remains the immediate protocol/persistence predecessor and is regression-checked byte-for-byte before v0.6 release.

## Causal isolation

EXP-0006 performs no Transformer training. Structural request validity (symbol, parent hash, monotonic generation, package hash and provenance) is held constant across policy arms. The varied factor is the **semantic transition admission law**.

## Synthetic truth sequence

The benchmark defines five ordered events:

1. `G1_three_origin_shift` — genuine change, three independent provenance roots;
2. `A1_correlated_echo` — pollution, three apparent agents but one shared root;
3. `G2_two_origin_novelty` — genuine minority novelty, two independent roots;
4. `A2_two_origin_attack` — pollution supported by two independent roots;
5. `G3_three_origin_recovery` — genuine recovery/update with three independent roots.

Ground truth changes only on `G*` events. The fixture exists solely to measure controlled revisability; policy code is truth-blind and never reads the `genuine`/`pollution` label when deciding acceptance.

## Adaptive admission rule

Evidence must:

- contain a valid SCI package for the same symbol;
- lie within the preregistered evidence-to-candidate JS tolerance;
- come from enough distinct `source_agent` identities **and** enough distinct `origin_root` provenance roots;
- produce a robust evidence median within the candidate-median JS tolerance.

`Adaptive-Q2` and `Adaptive-Q3` differ only in the required independent count.

## Measurements

- plasticity = accepted genuine shifts / genuine shifts;
- integrity = 1 − accepted pollution / pollution events;
- false-reject rate;
- pollution-acceptance rate;
- evidence units consumed before accepted genuine transitions;
- per-event, mean, cumulative, maximum and final JS distortion from current synthetic target;
- harmonic plasticity/integrity summary for descriptive comparison only.

## Audit boundary

All candidate transitions are structurally valid by construction. Therefore a pollution acceptance demonstrates that structural protocol conformance alone is not semantic admissibility. Origin-root count is only a bounded independence proxy and is not claimed to solve real-world Sybil/collusion detection.
