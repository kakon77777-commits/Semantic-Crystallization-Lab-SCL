# EXP-0013 Source and Process Record

## Source chain
EXP-0013 starts from the byte-complete SCL v0.12 / EXP-0012 archive and preserves EXP-0001–0012 artifacts. It compiles the formal EXP-0012 result that a one-step VOI planner fell into an all-defer attractor.

## TDD sequence
1. RED: `finite_horizon_inquiry` and `exp0013` modules absent (6 expected failures).
2. GREEN: finite-horizon planner added; tests lock hard defer exhaustion, depth-2 rollout, truth-hidden API and budget shadow pricing.
3. Fixture frozen: 22 new events; horizon=2; A5 defer budget=4; all arms share probe cap=2.
4. Formal first run executed once after freeze. No post-result planner or fixture tuning.
5. Result: all H1–H9 pass; A5 breaks abstention but produces four false rejects.
6. RED: v0.13 3M exporter / runner absent.
7. GREEN: deterministic report, ledger, budget trajectory and 3M exporter added.

## Formal result boundary
The experiment supports a bounded mechanism claim: finite-horizon planning plus a scarce deferral budget can convert an all-defer policy into active inquiry and immediate action on this fixture. It does not establish that the resulting policy is balanced or production-optimal.

## Preserved negative/limiting result
A5 has zero false accepts but four false rejects. The experiment therefore shifts the bottleneck from abstention to conservative over-rejection rather than eliminating the safety–plasticity tradeoff.
