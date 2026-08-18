# Semantic Crystallization Lab (SCL)

**Semantic Crystallization Lab** is an EveMissLab research-and-engineering repository for finite semantic crystallization experiments: progressively re-basing reusable semantic structure into newly defined lexemes/operators while preserving explicit expansion contracts and measuring the cost of the shared dictionary that makes those lexemes meaningful.

The central engineering distinction is:

$$
\text{address compression} \neq \text{structural semantic crystallization}
$$

A one-word title or pointer is not counted as structural compression merely because it is short. SCL requires an explicit, inspectable decomposition and a reuse/generativity gate.

## Current milestone

**SCL v0.7 / EXP-0007 — Adaptive Epistemic Admission / Learning When to Trust**

EXP-0007 asks whether the admissibility threshold itself can adapt from delayed evidence rather than staying fixed at Q2 or Q3. The learned policy never sees the current event's truth label: it maintains Beta reliability posteriors for provenance roots from one-event-delayed validation feedback, then combines trust-weighted support with current risk, semantic novelty and recent pollution prevalence.

Across a 15-event deterministic sequence with source drift, Static-Q2 remains maximally plastic but accepts 5/6 pollution events; Static-Q3 keeps integrity at 0.833 but accepts only 5/9 genuine updates. Learned-Adaptive accepts 7/9 genuine updates and 1/6 pollution events, matching Q3 integrity while increasing plasticity from 0.556 to 0.778. Its risk-weighted cumulative target JS is `0.06780`, about 5.6% below Static-Q3 (`0.07184`) and far below Static-Q2 (`0.23379`).

The gain is not oracle behavior. A previously trusted A/B/C coalition still passes one later attack before delayed negative feedback lowers reputation. Root B moves from phase-1 trust `0.714` to final `0.455`, while emerging root D rises from `0.500` to `0.667`. The experiment therefore identifies **epistemic hysteresis**: trust can lag both genuine source emergence and source compromise.

See `experiments/EXP-0007/results/report.md`, `experiments/EXP-0007/results/trust_trajectory.jsonl`, and `experiments/EXP-0007/3m/`.

---

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

Reproduce:

```bash
python -m pytest -q
npm test
python scripts/run_exp0003.py
```

See `experiments/EXP-0003/results/report.md`, `experiments/EXP-0003/3m/`, and the v0.3 design/plan under `docs/superpowers/`. This remains a finite transparent toy-model mechanism experiment; it does not expose proprietary-model hidden states or prove a universal semantic fixed point.

---

### Previous milestone: SCL v0.2 / EXP-0002 — Bidirectional Symbol–Feature Localization

EXP-0002 established the immediately preceding result: `qevra` gained broader learned feature localization and better reverse retrieval while raw hidden-coordinate breadth did not monotonically increase. Its formal report remains at `experiments/EXP-0002/results/report.md`.

### Previous milestone: SCL v0.1 / EXP-0001 — Finite Semantic Crystallization

EXP-0001 starts from a 358-code-point Chinese passage selected from *內容信息上下界無限原理：認識論猜想* and constructs the following finite chain:

```text
L0  source Chinese prose                         358 code points
L1  controlled Chinese                          149 code points
L2  base semantic IR                            128 code points
L3  reusable composite-operator IR               74 code points
L4  qevra                                         5 code points
```

Surface-only terminal compression is therefore:

$$
C_{surface} = \frac{358}{5} = 71.6
$$

But the first-use dictionary-aware package is larger than the source. With the complete v0.1 atom/lexicon definition payload, the measured terminal ratio is approximately:

$$
C_{dictionary} \approx 0.105886
$$

That is intentional and important: EXP-0001 does **not** hide vocabulary-definition cost. Under the experiment's simplified fixed-dictionary amortization model, the terminal layer becomes code-point-positive after about 10 comparable documents reuse the same dictionary. This is only an amortization illustration; a real multi-document corpus experiment is a later milestone.

## Experimental lexemes

- `narel(x,y,m,o)` — two representations share meaning while their cognitive paths differ for observer `o`.
- `vek(x,m,b)` — a finite representation probes meaning under boundary `b`.
- `vesh(x,m,b)` — a representation reaches meaning under an admissibility boundary.
- `qevra` — the context-bound terminal crystallization of EXP-0001.

These lexemes are namespace-scoped experiment objects. Their semantics come from `experiments/EXP-0001/lexicon/lexicon.json`, not from spelling or external convention.

## What EXP-0001 currently demonstrates

- recursive expansion from `qevra` to base semantic IR;
- recovery of all 8 manually declared source invariants;
- strict surface shortening across the checked-in levels;
- explicit separation of surface ratio and dictionary-aware ratio;
- rejection of direct source-prose embedding in the lexicon;
- reuse of `narel` and `vesh` in a novel code-oriented composition not present in the source passage.

It does **not** prove the stronger ontological/cardinality claims of the source papers, automatic semantic discovery, or automatic human comprehension of invented lexemes.

## Reproduce

Requires Node.js 20+ and no third-party runtime dependencies.

```bash
npm test
npm run exp:0001
```

Generated outputs:

- `experiments/EXP-0001/results/metrics.json`
- `experiments/EXP-0001/results/report.md`

## Repository map

```text
docs/superpowers/specs/       experiment design/specification
docs/superpowers/plans/       implementation plan
papers/source-original/       preserved source papers and EML-U reference package
experiments/EXP-0001/source/  source passage
experiments/EXP-0001/semantic-ir/ explicit atoms and invariant map
experiments/EXP-0001/lexicon/ new lexemes and expansion graph
experiments/EXP-0001/chain/   checked-in compression levels
experiments/EXP-0001/results/ reproducible metrics/report
experiments/EXP-0002/        neural symbol-feature localization experiment and bounded 3M outputs
experiments/EXP-0003/        semantic-basin stabilization, memory attention, ablations, and 3M outputs
experiments/EXP-0004/        cross-agent SCI reconstruction, transfer, correction, contamination stress, ledger, and 3M outputs
experiments/EXP-0005/        protocol × persistence continuity, restart/fault audit, and 3M outputs
experiments/EXP-0006/        admissible cognitive transitions and plasticity–integrity frontier
experiments/EXP-0007/        adaptive epistemic admission, provenance trust drift, and delayed-feedback audit
python/scl_exp/              transparent neural/grid/3M experiment helpers
tests_py/                    Python unit and experiment-mechanics tests
src/                          generic validator/expander/metrics functions
test/                         Node built-in tests
scripts/                      deterministic experiment runners
```

## Design boundary

SCL deliberately keeps finite experiment boundaries explicit. These runs demonstrate mechanisms and measured trends; they do not by themselves establish the stronger ontological/cardinality claims of the source papers.
