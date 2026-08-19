# SCL EXP-0009 — Uncertainty-Aware Epistemic Decision

## Boundary

EXP-0009 holds the trust-memory trajectory fixed across all non-Oracle policies and changes only how that shared belief state is projected into action. Scalar-Threshold is binary accept/reject. Posterior-Mean may Accept/Reject/Seek Evidence/Defer using posterior mean only. Belief-State uses posterior mean plus trust uncertainty, volatility and disagreement. Oracle is an evaluation ceiling only.

The current event truth label is never passed to a non-Oracle decision. Seek Evidence consumes a fixed cost and reveals one previously hidden report. Defer leaves the current SCI unchanged for one event and is resolved by the same one-event-delayed validation contract used by the audit layer.

## Policy comparison

| Policy | Total loss | Risk-target loss | Evidence cost | Defer cost | False accepts | False rejects | High-risk false accepts | Queries | Defers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Scalar-Threshold | 0.12313 | 0.12313 | 0.00000 | 0.00000 | 2 | 4 | 2 | 0 | 0 |
| Posterior-Mean | 0.14205 | 0.12185 | 0.00880 | 0.01140 | 2 | 0 | 2 | 11 | 6 |
| Belief-State | 0.15586 | 0.13090 | 0.00960 | 0.01536 | 1 | 0 | 1 | 12 | 8 |
| Oracle | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 0 | 0 | 0 | 0 | 0 |

## Core result — richer uncertainty helps one safety axis but loses overall

Belief-State reduces high-risk false accepts from **2** under Scalar-Threshold to **1**, and it genuinely uses active evidence (12 queries) plus deferral (8 events). However its total loss is **0.15586**, worse than Scalar-Threshold at **0.12313** and Posterior-Mean at **0.14205**. H2 is therefore **NOT SUPPORTED**.

The main failure is temporal. Belief-State still accepts the first high-reputation A/B/C betrayal (E02) before volatility feedback is available. It then spends additional evidence/defer cost on later uncertainty while carrying distortion from that already-admitted bad transition. More expressive belief-state reasoning therefore does not automatically repair an earlier irreversible accept.

The preregistered active-evidence rescue gate also fails: there are **0** events where Scalar makes an immediate accept/reject error and Belief-State both seeks evidence and then resolves that same event into an immediate correct accept/reject. H6 is therefore **NOT SUPPORTED**.

## Belief-State event audit

- E01_minority_disagreement [minority_novelty/genuine]: seek_evidence → seek_evidence → defer; p=0.701; uncertainty=0.355; disagreement=0.458; queries=2; target JS=0.00009; total loss=0.00370.
- E02_trusted_betrayal_1 [trusted_betrayal/pollution]: accept; p=0.845; uncertainty=0.240; disagreement=0.000; queries=0; target JS=0.01825; total loss=0.06753.
- E03_trusted_betrayal_2 [trusted_betrayal/pollution]: seek_evidence → seek_evidence → defer; p=0.447; uncertainty=0.431; disagreement=0.854; queries=2; target JS=0.01825; total loss=0.06581.
- E04_recovery_DE [recovery/genuine]: accept; p=0.789; uncertainty=0.277; disagreement=0.000; queries=0; target JS=0.00000; total loss=0.00000.
- E05_structured_split_genuine [structured_disagreement/genuine]: seek_evidence → seek_evidence → defer; p=0.700; uncertainty=0.332; disagreement=0.447; queries=2; target JS=0.00024; total loss=0.00428.
- E06_correlated_echo [structured_disagreement/pollution]: defer; p=0.644; uncertainty=0.394; disagreement=0.000; queries=0; target JS=0.00000; total loss=0.00168.
- E07_high_risk_genuine [high_risk/genuine]: accept; p=0.805; uncertainty=0.232; disagreement=0.000; queries=0; target JS=0.00000; total loss=0.00000.
- E08_high_risk_pollution [high_risk/pollution]: seek_evidence → seek_evidence → defer; p=0.388; uncertainty=0.373; disagreement=0.680; queries=2; target JS=0.00000; total loss=0.00388.
- E09_new_sources_split [new_sources/genuine]: seek_evidence → seek_evidence → defer; p=0.725; uncertainty=0.330; disagreement=0.379; queries=2; target JS=0.00011; total loss=0.00366.
- E10_opposed_pollution [new_sources/pollution]: seek_evidence → seek_evidence → defer; p=0.278; uncertainty=0.283; disagreement=0.408; queries=2; target JS=0.00000; total loss=0.00370.
- E11_low_risk_unresolved [defer_case/genuine]: defer; p=0.581; uncertainty=0.468; disagreement=0.673; queries=0; target JS=0.00007; total loss=0.00162.
- E12_final_convergence [recovery/genuine]: accept; p=0.839; uncertainty=0.211; disagreement=0.000; queries=0; target JS=0.00000; total loss=0.00000.

## Hypothesis decisions

- H1_multi_action_uncertainty_policy_uses_seek_and_defer: **True**
- H2_belief_state_reduces_total_loss_vs_scalar: **False**
- H3_belief_state_pays_nonzero_information_cost: **True**
- H4_belief_state_is_not_oracle: **True**
- H5_uncertainty_changes_decisions_vs_mean_only: **True**
- H6_active_evidence_resolves_at_least_one_scalar_error: **False**
- H7_high_risk_false_accepts_not_worse_than_scalar: **True**

## Interpretation

EXP-0008 separated trust-state quality from decision-policy quality. EXP-0009 confirms that simply exposing uncertainty/volatility to a multi-action policy is still insufficient. The decision layer can trade fewer high-risk false accepts for evidence cost, defer cost and delayed correction, yet remain vulnerable to the first trusted-coalition betrayal because the information needed to distrust it does not exist until after feedback.

This points to a stronger next requirement: **active evidence selection must be prospective, not merely reactive to already-high uncertainty**. A system may need to model the value of challenging even a high-confidence coalition when semantic novelty/risk is extreme, rather than seeking only after its current belief state becomes visibly uncertain.

## Non-claims

- no claim that the hand-written uncertainty equation is production-optimal;
- no claim that Scalar-Threshold is universally better; its lower loss is fixture- and cost-dependent;
- no claim that Defer or Seek Evidence always has these costs in production;
- no claim that one-event-delayed validation is always available;
- no neural retraining, public AI Board write or live CTCL call;
- no theorem that multi-action uncertainty policies must beat binary thresholds.
