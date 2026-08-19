# EXP-0008 Source and Process Record

## Inputs

- canonical EXP-0004 merged `qevra` SCI package in shared F01–F19 feature coordinates;
- EXP-0007 admission equation and one-event-delayed validation convention;
- no neural retraining.

## Experimental isolation

The three deployable policies share exactly the same event stream, risk values, novelty calculation, recent-pollution term, minimum independent-origin rule and required-support equation. The only intervention is the memory dynamics used to maintain provenance trust.

## TDD sequence

1. RED: missing `trust_dynamics` module.
2. GREEN: cumulative/fixed/adaptive decay primitives; betrayal and recovery asymmetry.
3. RED: missing common trust-dynamics admission policy.
4. GREEN: same required-support equation across all three modes; delayed-feedback-only trust update.
5. RED: missing EXP-0008 online benchmark.
6. GREEN: 20-event calibration/cold-start/betrayal/recovery/concept-drift sequence.
7. RED: missing v0.8 3M exporter/runner.
8. GREEN: deterministic report, event ledger, trust trajectory, 3M checksum domain and verification.

## Outcome discipline

H4 (adaptive risk loss beats cumulative) is retained as **false**. Two post-run findings are explicitly exploratory: Adaptive-Dynamics has the best trust Brier calibration while producing the exact same accept/reject sequence as Cumulative-History, and Fixed-Decay dominates this particular fixture.
