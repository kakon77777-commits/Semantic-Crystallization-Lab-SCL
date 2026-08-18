# EXP-0007 Source and Process Record

## Research question

Can an SCI admission policy learn **when to trust** rather than using a fixed Q2/Q3 evidence quorum?

## Causal boundary

EXP-0007 does not retrain the neural encoder. It consumes the canonical merged `qevra` SCI package from EXP-0004 and keeps the F01–F19 shared feature coordinate fixed.

The current truth label is evaluation-only. Learned-Adaptive receives feedback about event `t` only before deciding event `t+1`.

## Policies

1. `Static-Q2`: accept at two distinct provenance roots.
2. `Static-Q3`: accept at three distinct provenance roots.
3. `Learned-Adaptive`: Beta provenance reliability + risk + novelty + recent pollution.
4. `Oracle`: accepts genuine and rejects pollution; ceiling only.

## Online sequence

Fifteen deterministic events are split into:

- **calibration** — A/B initially become reliable, X is correlated echo noise, C/D are mixed;
- **drift** — B becomes compromised while D/E begin carrying genuine minority novelty;
- **stress** — a historically strong A/B/C coalition attacks before delayed feedback degrades its reputation, followed by D/E/F and A/D/E recovery.

## Measurements

- plasticity;
- integrity;
- false accept / false reject;
- target JS;
- risk-weighted cumulative target JS;
- provenance trust posterior drift;
- trust Brier score;
- dynamic required support and effective support per event;
- deterministic 3M projection and append-only compatibility ledger.

## Preserved negative evidence

The learned policy is not treated as universally successful. It false-rejects early low-reputation genuine novelty and later accepts one pollution event from a historically trusted coalition. These are retained as evidence of epistemic hysteresis rather than tuned away.
