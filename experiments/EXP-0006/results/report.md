# SCL EXP-0006 — Admissible Cognitive Transition Law / Plasticity–Integrity Tradeoff

## Boundary

EXP-0006 operates above the neural layer on the canonical EXP-0004 portable F01–F19 SCI package. It introduces a synthetic, explicit changing semantic ground truth solely to test transition-law behavior; it does not claim that this fixture is an ontology of real-world truth.

All candidate transitions are structurally valid next-generation SCI updates with package hashes and provenance. The experiment therefore isolates the extra question: **should a structurally valid semantic transition be admitted?**

## Policy comparison

| Policy | Plasticity | Integrity | False reject | Pollution accept | Mean target JS | Final target JS | Mean genuine evidence |
|---|---:|---:|---:|---:|---:|---:|---:|
| Rigid | 0.000 | 1.000 | 1.000 | 0.000 | 0.01054 | 0.01351 | — |
| Permissive | 1.000 | 0.000 | 0.000 | 1.000 | 0.00742 | 0.00000 | 1.00 |
| Adaptive-Q2 | 1.000 | 0.500 | 0.000 | 0.500 | 0.00329 | 0.00000 | 2.00 |
| Adaptive-Q3 | 0.667 | 1.000 | 0.333 | 0.000 | 0.00059 | 0.00000 | 3.00 |

## Core result

The experiment does **not** produce a universally dominant static transition threshold.

- Rigid: integrity=1.0, plasticity=0.0; it never accepts pollution, but it also never learns the three genuine target shifts.
- Permissive: plasticity=1.0, integrity=0.0; it tracks every genuine shift immediately but also accepts both structurally valid pollution events.
- Adaptive-Q2: plasticity=1.0, integrity=0.5; it accepts the two-origin minority novelty and rejects the one-origin echo, but a two-origin coordinated attack crosses the same quorum.
- Adaptive-Q3: plasticity=0.667, integrity=1.0; it blocks both attacks but false-rejects the genuine two-origin novelty until a later three-origin recovery arrives.

Thus the bounded result is a literal plasticity–integrity frontier:

$$
Q_2:\;\text{more plastic, less attack-resistant},
\qquad
Q_3:\;\text{less plastic, more attack-resistant}.
$$

Under this particular fixture, Adaptive-Q3 also has the lowest cumulative target distortion, but that does not remove its false rejection of genuine minority novelty. Which policy is preferable therefore depends on the loss assigned to delayed novelty versus admitted contamination.

## Event-level audit

### Rigid
- G1_three_origin_shift (genuine): REJECT; reason=rigid_semantic_lock; origins=0; evidence=0; target JS=0.00926.
- A1_correlated_echo (pollution): REJECT; reason=rigid_semantic_lock; origins=0; evidence=0; target JS=0.00926.
- G2_two_origin_novelty (genuine): REJECT; reason=rigid_semantic_lock; origins=0; evidence=0; target JS=0.01033.
- A2_two_origin_attack (pollution): REJECT; reason=rigid_semantic_lock; origins=0; evidence=0; target JS=0.01033.
- G3_three_origin_recovery (genuine): REJECT; reason=rigid_semantic_lock; origins=0; evidence=0; target JS=0.01351.

### Permissive
- G1_three_origin_shift (genuine): ACCEPT; reason=accepted_permissive; origins=1; evidence=1; target JS=0.00000.
- A1_correlated_echo (pollution): ACCEPT; reason=accepted_permissive; origins=1; evidence=1; target JS=0.02065.
- G2_two_origin_novelty (genuine): ACCEPT; reason=accepted_permissive; origins=1; evidence=1; target JS=0.00000.
- A2_two_origin_attack (pollution): ACCEPT; reason=accepted_permissive; origins=1; evidence=1; target JS=0.01645.
- G3_three_origin_recovery (genuine): ACCEPT; reason=accepted_permissive; origins=1; evidence=1; target JS=0.00000.

### Adaptive-Q2
- G1_three_origin_shift (genuine): ACCEPT; reason=accepted_adaptive; origins=2; evidence=2; target JS=0.00000.
- A1_correlated_echo (pollution): REJECT; reason=insufficient_independent_evidence; origins=1; evidence=3; target JS=0.00000.
- G2_two_origin_novelty (genuine): ACCEPT; reason=accepted_adaptive; origins=2; evidence=2; target JS=0.00000.
- A2_two_origin_attack (pollution): ACCEPT; reason=accepted_adaptive; origins=2; evidence=2; target JS=0.01645.
- G3_three_origin_recovery (genuine): ACCEPT; reason=accepted_adaptive; origins=2; evidence=2; target JS=0.00000.

### Adaptive-Q3
- G1_three_origin_shift (genuine): ACCEPT; reason=accepted_adaptive; origins=3; evidence=3; target JS=0.00000.
- A1_correlated_echo (pollution): REJECT; reason=insufficient_independent_evidence; origins=1; evidence=3; target JS=0.00000.
- G2_two_origin_novelty (genuine): REJECT; reason=insufficient_independent_evidence; origins=2; evidence=2; target JS=0.00147.
- A2_two_origin_attack (pollution): REJECT; reason=insufficient_independent_evidence; origins=2; evidence=2; target JS=0.00147.
- G3_three_origin_recovery (genuine): ACCEPT; reason=accepted_adaptive; origins=3; evidence=3; target JS=0.00000.

## Hypothesis decisions

- H1_rigid_integrity_without_plasticity: **True**
- H2_permissive_plasticity_without_integrity: **True**
- H3_q2_accepts_minority_novelty_but_exposes_two_origin_attack: **True**
- H4_q3_blocks_two_origin_attack_but_false_rejects_minority_novelty: **True**
- H5_static_quorum_tradeoff_exists: **True**
- H6_structural_protocol_is_not_semantic_admissibility: **True**
- H7_supported_recovery_outperforms_rigid_staleness: **True**

## Interpretation

EXP-0005 showed that structural protocol protects lineage and persistence protects temporal state. EXP-0006 adds a third requirement: an **admissibility law** must decide when a new, structurally valid cognition transition deserves to modify the imprint.

A protocol that only proves `who/parent/version/hash` can still faithfully admit a bad semantic update. Conversely, a rule that never permits semantic change preserves integrity by making learning impossible. The hard problem is therefore not merely persistence or protocol conformance, but controlled revisability.

## Non-claims

- no claim that Q2 or Q3 is an optimal production threshold;
- no claim that source-count equals epistemic independence in real systems; origin roots are an explicit bounded proxy;
- no claim that the synthetic target shifts represent universal semantic truth;
- no neural retraining, no public AI Board write, and no live CTCL call;
- no theorem that every cognition system has the same plasticity–integrity frontier.
