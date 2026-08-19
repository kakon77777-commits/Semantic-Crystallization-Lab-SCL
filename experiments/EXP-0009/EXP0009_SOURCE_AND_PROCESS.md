# EXP-0009 Source and Process Record

## Research question

Does exposing posterior uncertainty, volatility and disagreement to a multi-action epistemic policy improve SCI admission beyond a scalar trust threshold?

## Frozen boundary before result inspection

- all non-Oracle policies share the same Adaptive trust-memory trajectory;
- current event truth is hidden from non-Oracle decisions;
- trust feedback arrives one event late through an external audit trajectory;
- action space: `Accept`, `Reject`, `Seek Evidence`, `Defer`;
- `Seek Evidence` reveals one previously hidden report and pays a fixed cost;
- `Defer` keeps the current SCI for one event and resolves through delayed validation;
- Oracle sees truth only as an evaluation ceiling;
- no neural retraining, public AI Board write, or live CTCL call.

## TDD process

1. `test_epistemic_decision.py` was written first and failed because `epistemic_decision` did not exist.
2. Minimal belief aggregation and policy primitives were implemented until 5/5 tests passed.
3. `test_exp0009.py` was written first and failed because `exp0009` did not exist.
4. The deterministic 12-event benchmark and shared audit-trust trajectory were implemented until 4/4 tests passed.
5. 3M and runner tests were written before their implementations and failed on missing modules, then passed after minimal exporters/runners were added.

## Preregistered hypotheses

- H1 multi-action uncertainty policy uses both evidence seeking and deferral.
- H2 Belief-State reduces total loss versus Scalar-Threshold.
- H3 Belief-State pays nonzero information cost.
- H4 Belief-State remains worse than Oracle.
- H5 uncertainty changes decisions versus Posterior-Mean.
- H6 active evidence immediately resolves at least one Scalar error.
- H7 high-risk false accepts are not worse than Scalar.

## Result snapshot

Belief-State uses 12 evidence queries and 8 deferrals, and high-risk false accepts fall from 2 to 1. However total loss rises from Scalar `0.12313` to Belief-State `0.15586`; H2 is not supported. H6 is also not supported (`0` immediate scalar errors rescued into a correct immediate accept/reject after seeking). The strongest failure is E02: the first historically trusted A/B/C betrayal passes before negative feedback raises uncertainty.

## Interpretation discipline

The benchmark does not prove uncertainty-aware decision is generally harmful. It shows that **reactive** uncertainty awareness can be too late: once a high-confidence bad update has already been admitted, later uncertainty and active evidence may only add cost without undoing the earlier transition.
