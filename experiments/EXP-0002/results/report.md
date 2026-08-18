# SCL EXP-0002 — Bidirectional Symbol–Feature Localization

## Experimental boundary

This is a finite, supervised proof-of-mechanism on a transparent tiny PyTorch Transformer trained from scratch. It does not expose ChatGPT or proprietary-model hidden states and does not establish behavior of arbitrary foundation models.

After Stage 0 the entire semantic encoder and learned feature prototypes are frozen. Only the embedding rows of `qevra` and frequency-matched pointer control `tivak` may move during Stage 1 and Stage 2.

The three tested curriculum stages are:

1. Stage 0: `qevra` is in the vocabulary but receives no semantic training.
2. Stage 1: `qevra` receives only its compositional definition; the original source passage is forbidden from these rows.
3. Stage 2: `qevra` is reused in novel code, visual, multilingual and scientific contexts.

## Aggregate result across seeds

Seeds: `[11, 23, 37]`. Hidden width: `48`. Feature count: `19`. Support threshold: `0.5`.

| Metric | Stage 0 | Stage 1 | Stage 2 | Direction |
|---|---:|---:|---:|---|
| qevra feature support count | 3.333 | 11.333 | 13.333 | higher = broader |
| qevra effective feature support | 8.515 | 14.516 | 14.931 | higher = broader |
| qevra semantic recall | 0.143 | 0.643 | 0.762 | higher = better |
| qevra explicit-source target JS | 0.413 | 0.198 | 0.191 | lower = better |
| qevra semantic target separation | -0.017 | 0.144 | 0.149 | higher = better |
| qevra reverse round-trip top-1 | 1/3 | 3/3 | 3/3 | higher = better |
| qevra hidden effective dimension | 27.302 | 23.814 | 24.426 | measured, no assumed direction |
| qevra hidden active coordinates | 17.333 | 14.667 | 14.667 | measured, no assumed direction |
| tivak F19 pointer score | 0.118 | 0.514 | 0.696 | higher = pointer learned |
| tivak support count | 1.333 | 0.667 | 1.000 | narrow control expected |

## Hypothesis decisions

- Feature-localization growth: **SUPPORTED in this bounded model**.
- Bidirectional feature→symbol round-trip growth: **SUPPORTED in this bounded model**.
- Naive hidden-coordinate-growth claim: **NOT SUPPORTED**.
- Frequency-matched pointer control remains semantically narrow while learning pointer identity: **SUPPORTED**.
- Composite-symbol breadth (`qevra` broader than each lower-order child lexeme): **SUPPORTED**.

### Stage-2 lexeme breadth ladder

| Lexeme | Mean feature support | Mean effective feature support |
|---|---:|---:|
| narel | 5.000 | 9.578 |
| vek | 6.333 | 9.545 |
| vesh | 3.667 | 9.369 |
| qevra | 13.333 | 14.931 |
| tivak (pointer) | 1.000 | 3.907 |

The important distinction is that semantic feature coverage grew while raw hidden-coordinate breadth did not. In this model, a richer symbol behaved more like a **more selective address into a learned distributed feature space** than a token that simply turns on more hidden coordinates.

## Interpretation

The experiment supports a bounded form of SCL's symbol-localization claim: a single held-out lexeme can be moved into a pre-existing semantic feature space using only compositional definition and contextual reuse, and its feature signature can become substantially closer to the explicit semantic target of the much longer source passage.

It does not show that semantic content is literally equal to the number of activated neural dimensions. The measured hidden effective dimension and RMS-relative active-coordinate count did not increase monotonically. That naive interpretation is therefore rejected by this run.

## 3M output

The `3m/` directory stores a bounded matrix-ledger projection:

- MLF role: coordinates, matrices, provenance, explicit loss reports and checksums;
- MMR role: row traversal from symbols to features and column traversal from features to symbols;
- MMLC role: deterministic projection, JS distortion, support and round-trip calculations.

The output intentionally states `bounded-profile-not-formal-mlf-1.0`; the official MLF compiler was not executed here.

## Per-seed compact results

### Seed 11
- Stage 0: qevra support=3, semantic recall=0.071, explicit-target JS=0.550, hidden active=19, round-trip rank=5; tivak F19=0.002.
- Stage 1: qevra support=5, semantic recall=0.214, explicit-target JS=0.369, hidden active=13, round-trip rank=1; tivak F19=0.071.
- Stage 2: qevra support=8, semantic recall=0.429, explicit-target JS=0.332, hidden active=15, round-trip rank=1; tivak F19=0.726.

### Seed 23
- Stage 0: qevra support=0, semantic recall=0.000, explicit-target JS=0.357, hidden active=16, round-trip rank=5; tivak F19=0.016.
- Stage 1: qevra support=16, semantic recall=0.929, explicit-target JS=0.114, hidden active=16, round-trip rank=1; tivak F19=0.682.
- Stage 2: qevra support=17, semantic recall=1.000, explicit-target JS=0.104, hidden active=16, round-trip rank=1; tivak F19=0.643.

### Seed 37
- Stage 0: qevra support=7, semantic recall=0.357, explicit-target JS=0.333, hidden active=17, round-trip rank=1; tivak F19=0.336.
- Stage 1: qevra support=13, semantic recall=0.786, explicit-target JS=0.111, hidden active=15, round-trip rank=1; tivak F19=0.788.
- Stage 2: qevra support=15, semantic recall=0.857, explicit-target JS=0.135, hidden active=13, round-trip rank=1; tivak F19=0.720.

## Non-claims

- no claim about proprietary LLM hidden states;
- no claim that 3 seeds establish population-level generality;
- no claim that the manually specified feature catalog is the unique or complete semantic decomposition;
- no claim that feature-prototype activation is identical to biological or foundation-model attention;
- no cardinality or ontological claim from the source papers is proven here.
