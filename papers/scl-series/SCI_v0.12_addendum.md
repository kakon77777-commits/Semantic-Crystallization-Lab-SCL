# SCI v0.12 Addendum — Abstention Is Not Autonomy

EXP-0012 adds a bounded governance distinction to the SCI line:

$$
\text{epistemic safety by abstention} \neq \text{autonomous epistemic resolution}.
$$

A system can minimize short-horizon semantic damage by deferring every uncertain transition. If delayed validation is cheap, this can even dominate a more active closed-loop policy on scalar total loss while producing zero immediate resolution.

The experiment therefore separates three quantities that should not be collapsed:

1. semantic target loss;
2. information/latency cost;
3. autonomy / immediate-resolution rate.

A one-step value-of-information objective can have multiple policy attractors—defer-heavy, inquiry-heavy, or reject-heavy—depending on how future resolution and abstention are valued. The next SCI governance layer should model a multi-step inquiry horizon and bounded deferral budget rather than treating `Defer` as an effectively terminal cheap action.

This is an experimental addendum, not a universal theorem or production calibration.
