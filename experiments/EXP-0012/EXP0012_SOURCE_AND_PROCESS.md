# EXP-0012 Source and Process Record

## Source chain

EXP-0012 is a bounded extension of EXP-0011. It consumes the existing SCL F01–F19 feature substrate, the canonical EXP-0004 merged `qevra` SCI, one-event-delayed trust mechanics, the EXP-0011 opponent likelihood table, and the same three probe channels.

## Design approval

The user approved the next stage as **Autonomy Under Epistemic Pressure / Active Inquiry Resolution**. Before implementation, the comparison was fixed as A2 / A3 / A4 / Oracle and A3/A4 were constrained to the same probe set, costs, trust snapshots, likelihood table, and two-probe budget.

## TDD chronology

1. RED: `active_inquiry` module absent.
2. GREEN: autonomy artifact pack, one-step expected-loss inquiry planner, truth-free decision API, and exhausted-probe immediate-reject guard.
3. RED: EXP-0012 simulator absent.
4. GREEN: new 20-event fixture, shared trust snapshots, A2/A3/A4/Oracle comparison, preregistered H1–H8.
5. Formal first run frozen: A4 = 20/20 defer, 0 probes. H2/H3/H6 fail; H4/H5 pass numerically.
6. Post-hoc exploratory sensitivity only: defer/probe internal utility grid reveals abstention, inquiry-window, and reject-heavy regimes. Main arm and H1–H8 unchanged.
7. RED→GREEN: v0.12 3M exporter and deterministic runner; runner path contract regression fixed by restoring repo-root `sys.path` injection used by prior runners.

## Primary negative result

A4's one-step local planner values cheap delayed validation below immediate action or information acquisition at the frozen initial belief states. Therefore:

$$
\text{low scored loss} \not\Rightarrow \text{high autonomy}
$$

and

$$
\text{epistemic safety by abstention} \neq \text{autonomous epistemic resolution}.
$$

## Exploratory observation

Changing only planner penalties after the primary result produces three qualitative regions: defer attractor, a narrow inquiry window, and reject-heavy attractor. This is diagnostic, not preregistered evidence.

## Boundaries

- no current truth passed to non-Oracle policies;
- no neural retraining;
- no public AI Board write;
- no live CTCL call;
- exact candidate-hash reuse from earlier SCL experiments prohibited;
- post-hoc sensitivity cannot revise primary hypotheses.
