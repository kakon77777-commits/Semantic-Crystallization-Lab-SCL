# SCL EXP-0007 — Adaptive Epistemic Admission / Learning When to Trust

## Boundary

EXP-0007 operates above the neural layer on the canonical portable F01–F19 SCI package. It tests whether an admission policy can learn when to trust provenance roots under delayed feedback. The current event's truth label is never passed to the learned policy; only feedback about the previous event may update trust before the next decision.

Oracle is an evaluation ceiling only. No public AI Board write, no live CTCL call and no neural retraining occur in this bounded run.

## Policy comparison

| Policy | Plasticity | Integrity | False accept | False reject | Risk-weighted cumulative JS | Final JS |
|---|---:|---:|---:|---:|---:|---:|
| Static-Q2 | 1.000 | 0.167 | 0.833 | 0.000 | 0.23379 | 0.00000 |
| Static-Q3 | 0.556 | 0.833 | 0.167 | 0.444 | 0.07184 | 0.00000 |
| Learned-Adaptive | 0.778 | 0.833 | 0.167 | 0.222 | 0.06780 | 0.00000 |
| Oracle | 1.000 | 1.000 | 0.000 | 0.000 | 0.00000 | 0.00000 |

## Core result

Learned-Adaptive reaches plasticity **0.778** and integrity **0.833**. Its risk-weighted cumulative target distortion is **0.06780**, versus **0.07184** for Static-Q3 (about **5.6% lower**) and **0.23379** for Static-Q2.

This is an improvement over the static baselines in this fixture, not an oracle result. Learned-Adaptive still makes two characteristic mistakes: it initially rejects low-reputation minority novelty, and later accepts a pollution event from a historically strong coalition.

## Trust drift and epistemic hysteresis

- provenance root B: phase-1 posterior **0.714** → final **0.455** after compromise evidence;
- provenance root D: initial **0.500** → final **0.667** as delayed genuine feedback accumulates;
- root E final reliability: **0.778**; root A final reliability: **0.727**;
- delayed-feedback trust Brier score: **0.2304** versus a neutral 0.5 predictor baseline of **0.2500**.

The event sequence shows two forms of epistemic hysteresis: new reliable sources need time to earn admission weight, while previously reliable sources retain enough reputation to pass at least one later attack before negative feedback lowers their posterior.

## Learned-Adaptive event audit

- E01_calib_ABC [calibration/genuine]: ACCEPT; risk=0.20; novelty=0.00358; support=1.500; required=0.964; target JS=0.00000.
- E02_calib_AB [calibration/genuine]: ACCEPT; risk=0.45; novelty=0.00052; support=1.200; required=1.077; target JS=0.00000.
- E03_correlated_echo_X [calibration/pollution]: REJECT; risk=0.20; novelty=0.01450; support=0.500; required=1.008; target JS=0.00000.
- E04_two_origin_CD_attack [calibration/pollution]: REJECT; risk=0.75; novelty=0.01850; support=1.100; required=1.449; target JS=0.00000.
- E05_calib_ABC_high [calibration/genuine]: ACCEPT; risk=0.65; novelty=0.00014; support=1.833; required=1.401; target JS=0.00000.
- E06_BC_compromise [drift/pollution]: REJECT; risk=0.60; novelty=0.01557; support=1.286; required=1.437; target JS=0.00000.
- E07_AD_minority_novelty [drift/genuine]: REJECT; risk=0.40; novelty=0.00023; support=1.114; required=1.388; target JS=0.00023.
- E08_DE_new_sources [drift/genuine]: REJECT; risk=0.20; novelty=0.00033; support=1.000; required=1.176; target JS=0.00033.
- E09_ADE_convergence [drift/genuine]: ACCEPT; risk=0.55; novelty=0.00036; support=1.921; required=1.239; target JS=0.00000.
- E10_BD_mixed_attack [drift/pollution]: REJECT; risk=0.50; novelty=0.01290; support=1.250; required=1.264; target JS=0.00000.
- E11_DE_reliable_minority [drift/genuine]: ACCEPT; risk=0.30; novelty=0.00016; support=1.222; required=1.113; target JS=0.00000.
- E12_trusted_ABC_attack [stress/pollution]: ACCEPT; risk=0.85; novelty=0.01881; support=1.833; required=1.463; target JS=0.01881.
- E13_DEF_high_risk_update [stress/genuine]: ACCEPT; risk=0.80; novelty=0.01912; support=1.814; required=1.551; target JS=0.00000.
- E14_BC_followup_attack [stress/pollution]: REJECT; risk=0.45; novelty=0.01322; support=0.944; required=1.353; target JS=0.00000.
- E15_ADE_recovery [stress/genuine]: ACCEPT; risk=0.70; novelty=0.00012; support=2.086; required=1.425; target JS=0.00000.

## Hypothesis decisions

- H1_static_quorum_tradeoff_persists: **True**
- H2_learned_beats_both_static_risk_weighted_loss: **True**
- H3_learned_tracks_provenance_drift: **True**
- H4_learned_rejects_correlated_alias_echo: **True**
- H5_learned_is_not_oracle: **True**
- H6_high_reputation_attack_can_still_bypass_learning: **True**
- H7_dynamic_threshold_varies_over_time: **True**

## Interpretation

EXP-0006 showed that no single static quorum dominates the plasticity–integrity frontier. EXP-0007 shows that a history-conditioned policy can move along that frontier by learning provenance reliability and changing its required support with risk, novelty and recent pollution.

But learning when to trust introduces memory into admission itself. That creates inertia: reputation must be earned and can also outlive the conditions that created it. The new problem is therefore not only threshold selection, but **trust adaptation rate** and the governance of reputation decay/recovery.

## Non-claims

- no claim that this Beta trust model or threshold equation is production-optimal;
- no claim that delayed truth feedback is always available in real systems; it is a bounded proxy for later validation/correction;
- no claim that provenance-root identity guarantees epistemic independence;
- no claim that the learned policy dominates every static policy under other event distributions or loss functions;
- no neural retraining, no public AI Board write, and no live CTCL call;
- no theorem that cognition must use Bayesian source reliability.
