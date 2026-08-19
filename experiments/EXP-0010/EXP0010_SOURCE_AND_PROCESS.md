# EXP-0010 Source and Process Record

## Source chain

EXP-0010 starts from the byte-complete SCL v0.9 / EXP-0009 archive and keeps EXP-0001–0009 canonical artifacts unchanged. The experimental novelty is that earlier reports/validation records are now treated as a causal input to a later policy.

### Artifact sources actually read

- `experiments/EXP-0001/results/report.md` through `EXP-0009/results/report.md` (9 reports)
- `VALIDATION_V04.json` through `VALIDATION_V09.json` (6 validation records)

`reflexive_artifact.py` hashes every source and compiles meta-warning flags only from stored validation outcomes. It does not read EXP-0010 truth labels.

## TDD process

### RED 1 — artifact compiler

`tests_py/test_reflexive_artifact.py` first failed with `ModuleNotFoundError`. Minimal implementation added SHA-audited report/validation loading plus failure-chain compilation. Result: GREEN (2 tests).

### RED 2 — order-1 / order-2 challenge primitives

`tests_py/test_reflexive_challenge.py` first failed because the module did not exist. Minimal implementation added:

- A1 prospective challenge over the existing EXP-0009 Belief-State decision;
- A2 repeated-coalition / boundary-skimming challenge of A1's challenge rule.

Result: GREEN (2 tests).

### RED 3 — full two-phase experiment

`tests_py/test_exp0010.py` first failed because `exp0010` did not exist. The implementation added:

- 14 new events;
- Phase-I novel transfer and Phase-II meta-adversarial split;
- one shared trust snapshot sequence for A0/A1/A2;
- exact candidate-hash / event-ID memorization guard;
- pre-registered H1–H7 decisions.

Result: GREEN (3 tests).

### RED 4 — 3M and deterministic runner

`tests_py/test_three_m_v10.py` / `test_runner_exp0010.py` first failed because v0.10 exporter/runner did not exist. The implementation added bounded 3M matrices, action routes, artifact-source rows, append-only reflexive ledger, checksum verification and deterministic report generation.

Result: GREEN (2 tests).

## Frozen fixture / no post-result tuning

After the first complete benchmark run, the following outcome was observed and the fixture/rule thresholds were **not** retuned:

- H1: `True`
- H2: `True`
- H3: `True`
- H4: `True`
- H5: `False`
- H6: `True`
- H7: `True`

In particular, A2's failure was retained instead of modifying evidence reserves or the second-order trigger to force a positive result.

## Main measured outcome

### Phase I: artifact-conditioned transfer

- A0 novel-transfer loss: `0.1402591432`
- A1 novel-transfer loss: `0.0164684685`
- A1 caught A0 high-confidence error: `R10N01_trusted_consensus_pollution`

This is a bounded first-order reflexive lift on a newly instantiated fixture.

### Phase II: rule-aware environment

A1 is exploited on:

- `R10M01_boundary_skimming_attack`
- `R10M03_slow_roll_attack`
- `R10M06_low_signal_slow_roll`

A2 triggers a second-order challenge on M01 but the added evidence does not move the final decision away from `accept`; A2 therefore catches `0` A1 exploits and pays one extra evidence-query cost.

- A1 meta-phase loss: `0.0371987722`
- A2 meta-phase loss: `0.0379987722`

H5 is retained as a negative result.

## Memorization guard

The guard scans the previous experiment tree and found 286 distinct 64-hex artifact tokens. EXP-0010 candidate packages have **0 exact SHA overlaps**, and all EXP-0010 event IDs are absent from the prior corpus.

This does not claim the new fixture is semantically unrelated to previous work: structural homology is the deliberate transfer test.

## Interpretation boundary

The run demonstrates that a prior experiment chain can be made causally active in a later transparent decision system. It does not establish that an arbitrary future AI will spontaneously infer the same meta-rules from the repository, and it directly rejects a simple monotonic `higher reflexive order ⇒ better decisions` rule in this fixture.
