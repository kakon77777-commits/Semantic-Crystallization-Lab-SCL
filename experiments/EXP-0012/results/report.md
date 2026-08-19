# SCL EXP-0012 — Autonomy Under Epistemic Pressure / Active Inquiry Resolution

## Boundary

EXP-0012 keeps the EXP-0011 trust snapshots, opponent likelihood table, three probe channels, per-probe cost and two-probe cap fixed between A3 and A4. A4 adds only a value-of-information inquiry planner plus probe-conditioned immediate resolution. Current event truth is hidden from every non-Oracle policy.

The fixture and preregistered H1–H8 were frozen before the formal first run. The post-hoc sensitivity grid is explicitly exploratory and does not change the main arm or hypothesis decisions.

## Policy comparison

| Policy | Total loss | Target loss | False accepts | False rejects | Probes | Defers | Immediate resolution |
|---|---:|---:|---:|---:|---:|---:|---:|
| A2-Second-Order | 0.22122 | 0.21540 | 10 | 0 | 2 | 2 | 0.900 |
| A3-Closed-Loop-Deferred | 0.12862 | 0.09173 | 3 | 0 | 23 | 9 | 0.550 |
| A4-Active-Resolution | 0.03792 | 0.00039 | 0 | 0 | 0 | 20 | 0.000 |
| Oracle | 0.00000 | 0.00000 | 0 | 0 | 0 | 0 | 1.000 |

## Core result — the first active-inquiry planner collapses into abstention

The preregistered A4 arm issues **0** probes and defers **20/20** events. It therefore does not solve the autonomy objective. H2, H3 and H6 are **NOT SUPPORTED**.

This is not a runner failure: under the frozen internal expected-loss model, `Defer` has lower estimated loss than Accept, Reject or Probe at the initial belief states. The planner therefore enters a **defer attractor**. Because delayed validation is cheap in the benchmark, that abstention also keeps target distortion extremely low and makes H5 (total loss below A3) superficially true. That is precisely why total loss alone is not a sufficient autonomy metric.

The bounded separation is:

$$
\text{epistemic safety by abstention} \neq \text{autonomous epistemic resolution}.
$$

## Post-hoc sensitivity — three attractor regions

The exploratory grid varies only the planner's internal defer/probe penalties after the formal result was frozen. It reveals three qualitative regions: cheap defer produces near-total abstention; intermediate defer cost plus sufficiently cheap probes opens an inquiry window; high defer cost can jump directly into a reject-heavy regime. This is diagnostic only, not evidence for an optimized A4.

Representative rows:

| defer penalty | probe penalty | defers | probes | accepts | rejects | false rejects | total loss |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.33 | 0.035 | 20 | 0 | 0 | 0 | 0 | 0.03792 |
| 0.50 | 0.035 | 6 | 17 | 4 | 10 | 4 | 0.02671 |
| 0.50 | 0.010 | 1 | 24 | 2 | 17 | 6 | 0.02244 |
| 0.65 | 0.035 | 0 | 0 | 0 | 20 | 8 | 0.00233 |

The result suggests that inquiry planning needs an explicit model of **future resolution value / deferral budget / irreversible action cost**, not only a one-step expected-loss comparison.

## Hypothesis decisions

- H1_autonomy_pack_compiles_exp0011: **True**
- H2_a4_uses_active_inquiry_planning: **False**
- H3_a4_reduces_deferral_vs_a3: **False**
- H4_a4_target_loss_not_worse_than_a3: **True**
- H5_a4_total_loss_below_a3: **True**
- H6_a4_resolves_at_least_one_a3_defer_correctly: **False**
- H7_non_oracle_gap_remains: **True**
- H8_no_exact_candidate_reuse_from_prior_experiments: **True**

## Interpretation

EXP-0011 showed that closed-loop opponent modeling can buy safety by deferring. EXP-0012 shows that merely adding a one-step value-of-information planner does not automatically turn that safety into autonomy. When delayed validation is modeled as a cheap action, rational local optimization can prefer abstention everywhere; when abstention is made expensive, the policy can jump to over-rejection rather than useful inquiry.

The next mechanism should therefore treat inquiry as a **multi-step plan with a resolution horizon and a bounded deferral budget**, so the policy can compare `probe now → expected resolution later` against both irreversible action and the cumulative cost of continued abstention.

## Non-claims

- no claim that these internal planning penalties are production-calibrated;
- no claim that the exploratory sensitivity grid is preregistered evidence;
- no claim that A4 failure disproves active inquiry generally; it rejects this specific one-step planner;
- no neural retraining, public AI Board write or live CTCL call;
- no theorem that defer/inquiry/reject attractor regions occur in all agents.
