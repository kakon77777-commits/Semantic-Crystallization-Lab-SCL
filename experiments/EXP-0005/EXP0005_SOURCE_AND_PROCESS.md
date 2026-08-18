# EXP-0005 Source and Process Record

## Upstream source

EXP-0005 consumes only canonical EXP-0004 SCI outputs already stored in this repository:

- `experiments/EXP-0004/results/metrics.json` — independent qevra packages for agent-A/B/C;
- `experiments/EXP-0004/packages/merged_qevra.json` — accepted median correction reference;
- `experiments/EXP-0004/packages/contaminated_qevra.json` — correlated contamination package.

No source paper text is reinterpreted and no new semantic labels are generated in EXP-0005.

## Session process

For each arm and each agent:

1. Session 1 ends with the median qevra correction at protocol version 2.
2. Restart either restores that cognition state (persistence=yes) or resets to the agent's independent proposal (persistence=no).
3. A bootstrap correction is delivered.
4. The identical four-class fault set is delivered.
5. Protocol arms validate typed envelopes fail-closed; no-protocol arms use deterministic last-write-wins bare-package semantics.
6. Restart drift, correction retention, target JS, final cross-agent JS, fault outcomes and history continuity are recorded.

## Protocol implementation

`python/scl_exp/sci_protocol.py` implements canonical package/envelope hashing, provenance checks, monotonic versioning, parent checks, superseded-hash rollback rejection, idempotence and batch fork quarantine.

## Persistence implementation

`python/scl_exp/persistent_cognition.py` implements explicit cognition snapshots. Persistence preserves active package, version, accepted/superseded hash sets and history. Non-persistent restart intentionally returns to the independent SCI proposal and clears continuity history.

## Determinism

EXP-0005 itself is pure deterministic feature-space computation over canonical JSON artifacts. It performs no stochastic neural training.
