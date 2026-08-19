# SCL EXP-0013 — Finite-Horizon Epistemic Planning / Deferral-Budgeted Inquiry

## Boundary

EXP-0013 keeps the same shared trust snapshots, opponent likelihood table, three probe channels, per-probe cost and two-probe cap for A3/A4/A5. A5 adds only a depth-2 rollout over probe sequences plus a hard cross-event deferral budget of four. Current truth is hidden from all non-Oracle policies.

The 22-event fixture and H1–H9 were frozen before the formal first run. No post-result parameter tuning changes the primary arm.

## Policy comparison

| Policy | Total loss | Target loss | False accepts | False rejects | Probes | Defers | Immediate resolution |
|---|---:|---:|---:|---:|---:|---:|---:|
| A3-Closed-Loop-Deferred | 0.16585 | 0.13128 | 5 | 0 | 23 | 8 | 0.636 |
| A4-One-Step-VOI | 0.04182 | 0.00045 | 0 | 0 | 0 | 22 | 0.000 |
| A5-Finite-Horizon | 0.02663 | 0.00108 | 0 | 4 | 22 | 4 | 0.818 |
| Oracle | 0.00000 | 0.00000 | 0 | 0 | 0 | 0 | 1.000 |

## Core result — finite horizon plus a hard defer budget breaks the abstention attractor

A4 repeats the EXP-0012 pathology and defers **22/22** events with **0** probes. A5 instead uses **22** probes, consumes exactly **4/4** allowed deferrals and immediately resolves **81.8%** of events. Its maximum realized probe depth is **2**, so the depth-2 mechanism is actually exercised.

A5 total loss is **0.02663** versus A3 **0.16585** and A4 **0.04182**. It correctly converts **14** A4 deferrals into immediate accept/reject decisions.

All nine preregistered hypotheses are supported in this bounded fixture.

## New tradeoff — autonomy appears, but with over-rejection

A5 has **0** false accepts but **4** false rejects. The mechanism therefore does not eliminate the safety–plasticity tradeoff; it moves the system from abstention toward a safety-biased active policy. In particular, several benign/genuine updates are rejected while the budget is still preserved for later pressure.

This yields a new bounded separation:

$$
\text{breaking the defer attractor} \neq \text{balanced autonomous resolution}.
$$

## Hypothesis decisions

- H1_planning_pack_compiles_exp0012: **True**
- H2_a5_uses_multistep_inquiry: **True**
- H3_a5_breaks_a4_defer_attractor: **True**
- H4_a5_resolves_at_least_one_a4_defer_correctly: **True**
- H5_a5_target_loss_not_worse_than_a3: **True**
- H6_a5_total_loss_below_a3: **True**
- H7_a5_respects_hard_defer_budget: **True**
- H8_non_oracle_gap_remains: **True**
- H9_no_exact_candidate_reuse_from_prior_experiments: **True**

## Interpretation

EXP-0012 showed that a one-step value-of-information objective can make abstention locally optimal. EXP-0013 demonstrates a bounded counter-mechanism: finite probe rollout plus a scarce deferral budget assigns a shadow price to continued waiting, causing the policy to spend information budget and commit to immediate actions. The result is genuine autonomy relative to A4, but not yet balanced autonomy because the finite-horizon policy strongly prefers rejection under uncertainty.

The next mechanism should therefore optimize a constrained autonomy objective rather than only expected loss: for example, explicitly bound false-reject risk or preserve a minimum plasticity/acceptance rate while retaining the hard deferral budget.

## Non-claims

- no claim that horizon=2 or defer budget=4 is production-optimal;
- no claim that the internal loss model is calibrated to real-world consequences;
- no claim that zero false accepts is desirable if genuine novelty is systematically rejected;
- no neural retraining, public AI Board write or live CTCL call;
- no theorem that finite-horizon planning always breaks abstention attractors.
