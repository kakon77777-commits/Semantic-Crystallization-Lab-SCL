# EXP-0011 Source and Process Record

## Source chain
Uses the canonical SCL repository through EXP-0010. The closed-loop artifact compiler hashes all 10 prior reports and validations EXP-0004–0010.

## TDD record
1. `test_closed_loop_reflexive.py` first failed because `reflexive_strategy` did not exist.
2. Implemented the closed-loop rule pack, opponent Bayes filter, probe selection and A3 policy; tests turned green.
3. `test_exp0011.py` first failed because `exp0011` did not exist.
4. Implemented the 19-event stationary/switch/rapid-switch fixture and shared trust snapshots. A trust-snapshot integration failure exposed the old `reserve_reports` assumption; the v0.11 audit path was corrected to evaluate initial plus all probe-response sources symmetrically.
5. `test_three_m_v11.py` / `test_runner_exp0011.py` first failed because the v0.11 exporter/runner did not exist; both turned green after implementation.

## Frozen result
No fixture, likelihood-table or policy tuning occurred after the first formal run. All seven preregistered hypotheses are supported in this fixture. The main limitation is defer-heavy operation: A3 performs 21 probes and defers 13/19 events.

## Exploratory audit
Holding behavior fixed, A3/A2 information+latency costs reach approximate break-even only after a 10.06× uniform cost multiplier. This is exploratory, not preregistered.
