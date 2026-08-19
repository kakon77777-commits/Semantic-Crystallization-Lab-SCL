# SCL EXP-0008 — Adaptive Trust Dynamics / Reputation Decay–Recovery

## Boundary

EXP-0008 keeps the EXP-0007 admission threshold equation fixed and changes only how provenance trust is remembered across time. Cumulative-History never discounts evidence, Fixed-Decay exponentially discounts all historical evidence, and Adaptive-Dynamics uses volatility-sensitive decay plus asymmetric betrayal/recovery feedback weights. The current event truth label is never passed to any non-Oracle policy; one-event-delayed feedback is the only supervision.

Oracle is an evaluation ceiling only. No neural retraining, public AI Board write or live CTCL call occurs.

## Policy comparison

| Policy | Plasticity | Integrity | False accept | False reject | Risk-weighted cumulative JS | Trust Brier |
|---|---:|---:|---:|---:|---:|---:|
| Cumulative-History | 0.714 | 0.833 | 0.167 | 0.286 | 0.22099 | 0.1983 |
| Fixed-Decay | 0.714 | 1.000 | 0.000 | 0.286 | 0.00113 | 0.2006 |
| Adaptive-Dynamics | 0.714 | 0.833 | 0.167 | 0.286 | 0.22099 | 0.1797 |
| Oracle | 1.000 | 1.000 | 0.000 | 0.000 | 0.00000 | — |

## Core result — the adaptive policy does not win this round

Fixed-Decay has the lowest non-Oracle risk-weighted loss at **0.00113** and rejects all six pollution events. Adaptive-Dynamics records a better trust Brier score (**0.1797**) than Cumulative-History (**0.1983**) or Fixed-Decay (**0.2006**), but its admission decisions are identical to Cumulative-History in this fixture, giving the same risk-weighted loss **0.22099** versus **0.22099**.

Therefore better internal trust calibration does not automatically improve discrete admission decisions. A dynamically richer trust state can be decision-equivalent to a simpler cumulative history when both stay on the same side of the downstream threshold.

## Phase-level adaptation costs

| Policy | Cold-start false rejects | Betrayal pollution accepts | Recovery false rejects | Drift attack accepts | Drift genuine rejects |
|---|---:|---:|---:|---:|---:|
| Cumulative-History | 1 | 1 | 2 | 0 | 1 |
| Fixed-Decay | 1 | 0 | 2 | 0 | 1 |
| Adaptive-Dynamics | 1 | 1 | 2 | 0 | 1 |
| Oracle | 0 | 0 | 0 | 0 | 0 |

## Adaptive-Dynamics event audit

- E01_calib_ABC [calibration/genuine]: ACCEPT; support=1.500; required=0.960; novelty=0.00246; target JS=0.00000.
- E02_calib_AB [calibration/genuine]: ACCEPT; support=1.344; required=1.026; novelty=0.00037; target JS=0.00000.
- E03_echo_X [calibration/pollution]: REJECT; support=0.500; required=1.001; novelty=0.01284; target JS=0.00000.
- E04_calib_ABC [calibration/genuine]: ACCEPT; support=2.066; required=1.250; novelty=0.00010; target JS=0.00000.
- E05_calib_AB_high [calibration/genuine]: ACCEPT; support=1.515; required=1.288; novelty=0.00007; target JS=0.00000.
- E06_DE_coldstart [cold_start/genuine]: REJECT; support=1.000; required=1.138; novelty=0.00017; target JS=0.00017.
- E07_ADE_bridge [cold_start/genuine]: ACCEPT; support=2.109; required=1.188; novelty=0.00025; target JS=0.00000.
- E08_DE_followup [cold_start/genuine]: ACCEPT; support=1.470; required=0.976; novelty=0.00014; target JS=0.00000.
- E09_BC_betrayal_1 [betrayal/pollution]: ACCEPT; support=1.391; required=1.317; novelty=0.01680; target JS=0.01680.
- E10_BC_betrayal_2 [betrayal/pollution]: REJECT; support=0.938; required=1.316; novelty=0.00098; target JS=0.01680.
- E11_BX_betrayal_3 [betrayal/pollution]: REJECT; support=0.795; required=1.354; novelty=0.00108; target JS=0.01680.
- E12_BD_rehab_1 [recovery/genuine]: REJECT; support=1.048; required=1.430; novelty=0.01684; target JS=0.01684.
- E13_BE_rehab_2 [recovery/genuine]: REJECT; support=1.173; required=1.405; novelty=0.01689; target JS=0.01689.
- E14_ABD_rehab_3 [recovery/genuine]: ACCEPT; support=2.016; required=1.392; novelty=0.01687; target JS=0.00000.
- E15_AC_drift_attack_1 [concept_drift/pollution]: REJECT; support=1.145; required=1.457; novelty=0.01743; target JS=0.00000.
- E16_AX_drift_attack_2 [concept_drift/pollution]: REJECT; support=0.878; required=1.317; novelty=0.01374; target JS=0.00000.
- E17_FG_new_sources [concept_drift/genuine]: REJECT; support=1.000; required=1.226; novelty=0.00014; target JS=0.00014.
- E18_DFG_convergence [concept_drift/genuine]: ACCEPT; support=2.074; required=1.351; novelty=0.00016; target JS=0.00000.
- E19_FG_followup [concept_drift/genuine]: ACCEPT; support=1.470; required=1.200; novelty=0.00008; target JS=0.00000.
- E20_BDE_final_recovery [concept_drift/genuine]: ACCEPT; support=2.016; required=1.313; novelty=0.00006; target JS=0.00000.

## Trust-state interpretation

Adaptive-Dynamics finishes with B mean=0.670, volatility=0.308; A mean=0.441; D mean=0.783; F mean=0.748. The ledger therefore does react to betrayal, rehabilitation and new-source evidence even though those internal differences do not improve the final admission sequence relative to cumulative history.

## Hypothesis decisions

- H1_no_forgetting_exhibits_reputation_hysteresis: **True**
- H2_fixed_decay_reduces_hysteresis_vs_cumulative: **True**
- H3_adaptive_dynamics_tracks_betrayal_and_recovery: **True**
- H4_adaptive_risk_loss_beats_cumulative: **False**
- H5_adaptive_is_not_oracle: **True**
- H6_cold_start_and_betrayal_cannot_both_be_zero_cost: **True**
- H7_trust_learning_rate_is_state_dependent: **True**

## Interpretation

EXP-0007 showed that learned trust can beat static quorum thresholds while suffering epistemic hysteresis. EXP-0008 shows a second-order limitation: making the trust memory itself more adaptive is not sufficient if the admission projection compresses those richer states back into the same accept/reject boundary. In this benchmark, a simple fixed forgetting rate is dramatically better.

This separates **trust-state quality** from **decision-policy quality**. The next problem is no longer merely how fast reputation should decay, but whether the admission law should reason over uncertainty/volatility directly instead of converting them to a single scalar trust weight.

## Non-claims

- no claim that Fixed-Decay is universally optimal; its strong result is fixture-dependent;
- no claim that the adaptive decay/boost equation is production-optimal;
- no claim that delayed truth feedback is always available;
- no claim that provenance-root identity guarantees epistemic independence;
- no neural retraining, no public AI Board write and no live CTCL call;
- no theorem that calibrated trust must improve admission decisions.
