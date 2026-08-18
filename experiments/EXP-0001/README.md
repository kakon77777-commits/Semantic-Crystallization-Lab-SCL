# SCL-EXP-0001 — Finite Semantic Crystallization

## Question

Can a finite Chinese source passage be represented through progressively shorter layers of controlled prose, semantic IR, reusable composite operators, and finally one context-bound new lexeme, while keeping an explicit semantic expansion contract?

## Source

The 358-code-point source passage is selected verbatim from *內容信息上下界無限原理：認識論猜想*. The original DOCX is preserved in the downloadable experiment bundle; its SHA-256 is indexed under `papers/`.

## Chain

- `L0`: source prose.
- `L1`: controlled Chinese paraphrase.
- `L2`: base semantic IR.
- `L3`: composite-operator IR using newly defined `narel`, `vek`, and `vesh`.
- `L4`: `qevra`, a context-bound terminal crystallization.

`qevra` is not accepted as meaningful compression merely because it is short. Its full definition cost is counted, and it must recursively expand to the declared semantic invariants without consulting `source.zh.txt`.

## New lexemes

- `narel(x,y,m,o)`: two representations share meaning while their cognitive paths differ for observer `o`.
- `vek(x,m,b)`: a finite representation probes meaning under boundary `b`.
- `vesh(x,m,b)`: a representation reaches meaning under an admissibility boundary.
- `qevra`: the EXP-0001 terminal concept bundle.

These words have no semantics outside the checked-in namespace/lexicon unless another system explicitly imports the definitions.

## Anti-pointer rule

The recursive expander only returns semantic IR atoms. It has no path that reconstructs the original Chinese prose. Therefore the experiment does **not** obtain its result by storing the article inside the definition of `qevra`.

## Generativity control

The test suite instantiates `narel` and `vesh` with a code-optimization example that does not occur in the source passage. This tests whether the invented vocabulary acts as a reusable semantic basis rather than only as a title for one article.

## Interpretation

A successful run demonstrates a finite engineering construction with explicit invariants and costs. It does not establish the stronger ontological or cardinality claims of the source theory.
