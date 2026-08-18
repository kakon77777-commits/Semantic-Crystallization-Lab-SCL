# Semantic Crystallization Lab (SCL)

**Semantic Crystallization Lab** is an EveMissLab research-and-engineering repository for finite semantic crystallization experiments: progressively re-basing reusable semantic structure into newly defined lexemes/operators while preserving explicit expansion contracts and measuring the cost of the shared dictionary that makes those lexemes meaningful.

The central engineering distinction is:

$$
\text{address compression} \neq \text{structural semantic crystallization}
$$

A one-word title or pointer is not counted as structural compression merely because it is short. SCL requires an explicit, inspectable decomposition and a reuse/generativity gate.

## Current milestone

**SCL v0.2 / EXP-0002 — Bidirectional Symbol–Feature Localization**

EXP-0002 extends the finite crystallization chain into a transparent neural feature space. A tiny PyTorch Transformer first learns a fixed semantic feature space; after that freeze, only the embeddings of held-out crystallized lexeme `qevra` and frequency-matched pointer control `tivak` may move. Across seeds 11/23/37, `qevra` grows from a mean 3.333 thresholded features before semantic assignment to 13.333 after compositional definition plus contextual reuse, while semantic recall against the 14 source-derived features rises from 0.143 to 0.762 and explicit-target Jensen–Shannon distortion falls from 0.413 to 0.191. Reverse feature-to-symbol top-1 recovery rises from 1/3 to 3/3.

The naive stronger hypothesis is rejected: hidden effective dimension and RMS-relative active-coordinate count do not increase with semantic breadth. In this bounded model, crystallization looks more like selective localization of a broader learned feature bundle than simply turning on more hidden coordinates.

The Stage-2 breadth ladder is also explicit: mean thresholded support is `narel=5.0`, `vek=6.333`, `vesh=3.667`, `qevra=13.333`, and pointer-only `tivak=1.0`.

The GitHub audit branch stores the design, finite corpus, validation evidence, reported metrics and bounded 3M matrix-ledger projection. The separate byte-complete release ZIP also contains the executable Python source/tests and full raw per-seed hidden-vector ledger. To reproduce from that archive:

```bash
python -m unittest discover -s tests_py -v
python scripts/run_exp0002.py
```

See `experiments/EXP-0002/results/report.md` and `experiments/EXP-0002/3m/`. This is a finite toy-model mechanism experiment; it does not expose or claim hidden states from ChatGPT or any proprietary foundation model.

---

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
python/scl_exp/              transparent neural/grid/3M experiment helpers
tests_py/                    Python unit and experiment-mechanics tests
src/                          generic validator/expander/metrics functions
test/                         Node built-in tests
scripts/                      deterministic experiment runners
```

## Design boundary

SCL v0.1 is deliberately manual at the semantic-decomposition step. This makes the first experiment auditable: the system tests crystallization mechanics rather than hiding an unvalidated language-model judgment behind a compression score.
