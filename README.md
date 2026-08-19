# Semantic Crystallization Lab (SCL)

**Semantic Crystallization Lab** is an EveMissLab research-and-engineering repository for finite semantic crystallization experiments: progressively re-basing reusable semantic structure into newly defined lexemes/operators while preserving explicit expansion contracts and measuring the cost of the shared dictionary that makes those lexemes meaningful.

The central engineering distinction is:

$$
\text{address compression} \neq \text{structural semantic crystallization}
$$

A one-word title or pointer is not counted as structural compression merely because it is short. SCL requires an explicit, inspectable decomposition and a reuse/generativity gate.

## Current milestone

**SCL v0.8 / EXP-0008 — Adaptive Trust Dynamics / Reputation Decay–Recovery**

EXP-0008 holds the EXP-0007 admission equation fixed and varies only how provenance trust is remembered over time: cumulative history, fixed exponential decay, or volatility-sensitive adaptive decay with betrayal/recovery asymmetry. The 20-event online fixture includes source cold-start, repeated betrayal, rehabilitation and later provenance drift.

The strongest bounded result is a negative one: Adaptive-Dynamics has the best delayed-feedback trust Brier score (`0.1797`) but produces the same accept/reject sequence and the same risk-weighted loss (`0.22099`) as Cumulative-History. Fixed-Decay instead rejects all six pollution events and reaches risk-weighted loss `0.00113` in this fixture. Thus **better trust-state calibration does not imply better admission decisions** when richer trust states are projected through the same hard decision boundary.

See `experiments/EXP-0008/results/report.md`, `experiments/EXP-0008/EXP0008_SOURCE_AND_PROCESS.md`, and `experiments/EXP-0008/3m/`.

---

### Previous milestone: SCL v0.7 / EXP-0007 — Adaptive Epistemic Admission / Learning When to Trust

EXP-0007 learned provenance reliability under one-event-delayed feedback and modestly beat Static-Q3 on its synthetic risk-weighted benchmark while exposing epistemic hysteresis: new reliable roots needed time to earn trust, while historically trusted roots could retain enough reputation to pass a later attack.

### Previous milestone: SCL v0.6 / EXP-0006 — Admissible Cognitive Transition Law / Plasticity–Integrity Tradeoff

EXP-0006 asks what happens after protocol and persistence already exist: a persistent cognition must remain revisable, but a structurally valid update can still be semantically wrong. The experiment therefore holds structural validity constant and compares Rigid, Permissive, Adaptive-Q2 and Adaptive-Q3 admission laws across three synthetic genuine target shifts and two structurally valid pollution events.

The result is a bounded plasticity–integrity frontier. Rigid has integrity `1.0` but plasticity `0.0`; Permissive has plasticity `1.0` but integrity `0.0`; Adaptive-Q2 has plasticity `1.0` and integrity `0.5`; Adaptive-Q3 has integrity `1.0` but plasticity `0.667` because it false-rejects a genuine two-origin minority novelty. Q2 rejects the one-root correlated echo but accepts a two-origin coordinated attack; Q3 blocks both attacks but also blocks the two-origin genuine novelty until a later three-origin recovery.

Thus `who/parent/version/hash/provenance` is not enough by itself: **structural protocol validity is not semantic admissibility**, while an infinitely rigid admissibility law degenerates into an inability to learn. See `experiments/EXP-0006/results/report.md`, `experiments/EXP-0006/EXP0006_SOURCE_AND_PROCESS.md`, and `experiments/EXP-0006/3m/`.

---

### Previous milestone: SCL v0.5 / EXP-0005 — Protocol–Persistent Cognition Continuity

EXP-0005 isolates two continuity laws above the neural layer: **protocol** as inter-agent continuity and **persistence** as intra-agent continuity through time. Persistent arms reduce immediate restart JS from `0.0243` to `0.0000`, while protocol arms raise final correction retention under stale/provenance/rollback/fork faults from `0%` to `100%`.

Persistence without protocol survives restart but can still be overwritten; protocol without persistence can recover by valid bootstrap but does not eliminate the restart discontinuity itself. The no-protocol arms also demonstrate temporal false consensus: cross-agent JS reaches `0.0000` while target distortion becomes about `4.19×` worse.

See `experiments/EXP-0005/results/report.md` and `VALIDATION_V05.json`.

---

### Previous milestone: SCL v0.4 / EXP-0004 — Cross-Agent Symbolic Cognitive Imprint Transfer

EXP-0004 freezes the term **Symbolic Cognitive Imprint (SCI) / 符號認知印刻** and tests whether one symbol-conditioned semantic feature basin can be transferred and corrected across three independently initialized agents without assuming aligned raw hidden coordinates. The shared comparison space is the explicit F01–F19 feature coordinate only.

Key bounded result: single-donor transfer moves B/C 38.3% closer to donor A in feature-space JS, but receiver target distortion becomes 2.80× worse. A coordinate-wise median correction from three independent SCI proposals instead reduces cross-agent JS from 0.0559 to 0.0424 and mean target JS from 0.0526 to 0.0400. Thus agreement with one donor is not equivalent to semantic improvement.

The experiment also emits an append-only AI-Board-compatible SCI proposal/objection/correction ledger with CTCL-compatible logical sequence identifiers; it performs no public Board write and no live CTCL call.

See `papers/scl-series/SCI_v0.1.md`, `experiments/EXP-0004/results/report.md`, and `experiments/EXP-0004/3m/`.

---

### Previous milestone: SCL v0.3 / EXP-0003 — Semantic Basin Stabilization

EXP-0003 refines the AI-side hypothesis from “more semantic content means more active hidden coordinates” to a dynamic localization claim: a learned symbol should become a more stable address into a distributed semantic feature basin as it is repeatedly recalled, routed through memory, and learned across compatible contexts.

Across deterministic seeds `11/23/37`, the preregistered attentive-consolidation arm moves `qevra` from mean intrinsic context JS `0.0834` to `0.0588`, support Jaccard `0.6291` to `0.7207`, target recall `0.6181` to `0.7106`, centroid-to-target JS `0.0526` to `0.0356`, and cross-seed centroid JS `0.0559` to `0.0329`. The full preregistered directional gate passes on `2/3` seeds.

The ablations matter:

- repetition-only stabilizes strongly and, on pure stability metrics, is not beaten by diverse learning; `H2` is therefore a preserved negative result;
- memory-only assistance improves the current inference on `3/3` seeds while intrinsic metrics remain exactly unchanged, separating retrieval assistance from consolidation;
- attentive recall plus repeated learning transfers part of the external support back into the intrinsic symbol basin;
- after count-normalizing the `7` semantic vs `2` pointer memory entries, `qevra` preferentially routes toward semantic memory and `tivak` toward pointer memory on `3/3` seeds.

The bounded conclusion is not an infinite fixed point. It is directional evidence for:

$$
D_{\mathrm{ctx}}(s)\downarrow,\qquad J_{\mathrm{support}}(s)\uparrow
$$

under semantic consolidation, while target fidelity is tracked separately.

---

### Previous milestone: SCL v0.2 / EXP-0002 — Bidirectional Symbol–Feature Localization

EXP-0002 established that `qevra` gained broader learned feature localization and better reverse retrieval while raw hidden-coordinate breadth did not monotonically increase. Its formal report remains at `experiments/EXP-0002/results/report.md`.

### Previous milestone: SCL v0.1 / EXP-0001 — Finite Semantic Crystallization

EXP-0001 starts from a 358-code-point Chinese passage selected from *內容信息上下界無限原理：認識論猜想* and constructs a finite chain ending in the experimental lexeme `qevra`. Surface-only terminal compression is `71.6×`, while the first-use dictionary-aware package is larger than the source; the experiment intentionally keeps dictionary cost explicit.

## Experimental lexemes

- `narel(x,y,m,o)` — two representations share meaning while their cognitive paths differ for observer `o`.
- `vek(x,m,b)` — a finite representation probes meaning under boundary `b`.
- `vesh(x,m,b)` — a representation reaches meaning under an admissibility boundary.
- `qevra` — the context-bound terminal crystallization of EXP-0001.

## Reproduce

```bash
python -m pytest -q
npm test
python scripts/run_exp0008.py
```

## Repository map

```text
docs/superpowers/specs/       experiment design/specification
papers/source-original/       preserved source papers and EML-U reference package
experiments/EXP-0001/         finite semantic crystallization
experiments/EXP-0002/         neural symbol-feature localization
experiments/EXP-0003/         semantic-basin stabilization
experiments/EXP-0004/         cross-agent SCI transfer/correction
experiments/EXP-0005/         protocol × persistence continuity
experiments/EXP-0006/         admissible transition-law frontier
experiments/EXP-0007/         adaptive epistemic admission
experiments/EXP-0008/         adaptive trust-memory dynamics, decay, betrayal and recovery
python/scl_exp/               transparent experiment helpers
tests_py/                     Python TDD and regression tests
scripts/                      deterministic experiment runners
```

## Design boundary

SCL deliberately keeps finite experiment boundaries explicit. These runs demonstrate mechanisms and measured trends; they do not by themselves establish universal cognition laws or the stronger ontological/cardinality claims of the source papers.
