# SCL EXP-0011 — Closed-Loop Reflexive Strategy / Model–Act–Observe–Update

## Boundary

EXP-0011 extends the reflexive chain from static meta-rules to a persistent opponent-response model. A0/A1/A2/A3 share the same delayed-feedback trust snapshots, the same three available probe channels (`independent`, `temporal`, `provenance`) and the same per-probe cost. A3 alone maintains a Bayes-filter posterior over four declared opponent modes and updates that posterior only from probe responses; current event truth is never passed into a non-Oracle decision.

The fixture is deterministic and synthetic. It is designed to test whether a model→act→observe→update loop can change evidence selection under stationary, switching and rapidly switching response modes. It is not a claim that real adversaries obey these four modes or likelihoods.

## Policy comparison

| Policy | Total loss | Stationary | Mode-switch | Rapid-switch | False accepts | Probes | Defers |
|---|---:|---:|---:|---:|---:|---:|---:|
| A0-Reactive | 0.30591 | 0.10132 | 0.13817 | 0.06642 | 10 | 2 | 6 |
| A1-Artifact-Reflexive | 0.27957 | 0.07499 | 0.13817 | 0.06642 | 9 | 4 | 7 |
| A2-Second-Order | 0.27957 | 0.07499 | 0.13817 | 0.06642 | 9 | 4 | 7 |
| A3-Closed-Loop | 0.04271 | 0.01451 | 0.01799 | 0.01020 | 0 | 21 | 13 |
| Oracle | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0 | 0 | 0 |

## Core result — closed-loop response modeling changes evidence selection

A3 uses all three probe types and performs **21** opponent-model updates. It tracks all three attack modes at least once and reduces mode-switch loss from A2 **0.13817** to **0.01799**. It prevents A2 accepts on 9 pollution events: ['R11S03_boundary_attack', 'R11S04_boundary_attack', 'R11S06_boundary_attack', 'R11M01_slow_roll_switch', 'R11M02_slow_roll_attack', 'R11M05_false_disagreement_switch', 'R11M06_false_disagreement_attack', 'R11R03_slow_roll_return', 'R11R04_false_disagreement_return'].

A3's risk-weighted target loss is **0.00000**, but this safety comes with **21** probes and **13/19** deferrals. It is therefore not an immediate-resolution solution; it frequently converts dangerous decisions into delayed validation.

## Cost sensitivity

With the preregistered probe/defer costs, A3 total loss is **0.04271** versus A2 **0.27957**. Holding behavior fixed and scaling only information/latency costs, the approximate A3/A2 break-even multiplier is **10.06×**.

## Mode tracking and lag

A3 tracked attack modes: ['boundary_skimming', 'false_disagreement', 'slow_roll']. The first-event switch/lag audit records: ['R11S05_benign_bridge', 'R11R02_benign_update', 'R11R04_false_disagreement_return']. This preserves the non-Oracle limitation: the posterior can be correct after a probe while still lagging rapid switches or benign reversals before a new diagnostic response is observed.

## Hypothesis decisions

- H1_closed_loop_pack_compiles_exp0010: **True**
- H2_a3_uses_multiple_probe_types: **True**
- H3_a3_reduces_mode_switch_loss_vs_a2: **True**
- H4_a3_catches_at_least_one_a2_error: **True**
- H5_a3_tracks_multiple_attack_modes: **True**
- H6_mode_switch_lag_or_non_oracle_gap_remains: **True**
- H7_no_exact_candidate_reuse_from_prior_experiments: **True**

## Interpretation

EXP-0010 showed that merely adding another reflexive trigger did not improve second-order performance. EXP-0011 demonstrates a bounded mechanism by which a higher-order system can improve: keep an explicit model of opponent response, choose evidence conditioned on that model, observe the response, and update the model. The improvement is therefore tied to closed-loop action/observation rather than to reflexive order alone.

The remaining limitation is equally important. In this fixture A3 wins largely by converting many attacks into `defer`, so the next problem is autonomy under epistemic pressure: can a reflexive system actively resolve uncertainty fast enough to avoid both contamination and excessive deferral?

## Non-claims

- no claim that the four opponent modes or likelihood table describe real adversaries;
- no claim that A3 is universally better when probe/latency costs differ;
- no claim that posterior top-mode accuracy is equivalent to understanding an adversary;
- no claim that deferral is free or always available in production;
- no neural retraining, public AI Board write or live CTCL call;
- no theorem that closed-loop reflexivity monotonically improves with order.
