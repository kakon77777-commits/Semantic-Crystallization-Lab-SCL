# EXP-0001 Results — Finite Semantic Crystallization

## Status

The terminal lexeme `qevra` recursively expands to the complete declared semantic invariant set without embedding the original source prose in the lexicon. This is a finite engineering demonstration, not a proof of the source theory's stronger cardinality or ontological claims.

## Surface chain

- **L0** (source-prose): 358 code points
- **L1** (controlled-zh): 149 code points
- **L2** (base-semantic-ir): 128 code points
- **L3** (composite-operator-ir): 74 code points
- **L4** (context-bound-terminal-lexeme): 5 code points

The checked-in surface lengths are strictly decreasing: **yes**.

## Metrics

| Level | Kind | Surface code points | Dictionary code points | Package code points | Surface compression | Dictionary-aware compression |
|---|---|---:|---:|---:|---:|---:|
| L0 | source-prose | 358 | 0 | 358 | 1.000x | 1.000x |
| L1 | controlled-zh | 149 | 0 | 149 | 2.403x | 2.403x |
| L2 | base-semantic-ir | 128 | 824 | 952 | 2.797x | 0.376x |
| L3 | composite-operator-ir | 74 | 2329 | 2403 | 4.838x | 0.149x |
| L4 | context-bound-terminal-lexeme | 5 | 3376 | 3381 | 71.600x | 0.106x |

For the terminal level, surface-only compression is **71.600x**, while first-use dictionary-aware compression is **0.106x**. The distinction is intentional: a new vocabulary may be expensive on first use.

Under the simplified assumption that the same dictionary is reused across comparable documents, the terminal dictionary cost breaks even after **10** documents by code-point accounting. This is an amortization illustration, not yet a corpus result.

## Semantic invariant recovery

Declared invariants recovered: **8/8**.

Recall: **1.000**.

Missing: none.

Expanded base semantic IR:

```text
ISO(a,b,m);PATH(a,m,o,path[a]);PATH(b,m,o,path[b]);DIFF(path[a],path[b]);FINITE(c);PROBE(c,M);BOUND(M,P);MEAN(l,M);BOUND(M,P);MULTIEXP(m);BOUND(m,P);NEWTOPO(n);NOTSURFACE(r)
```

## Anti-pointer gate

- Source prose embedded in lexicon: **no**
- Source prefix embedded in lexicon: **no**
- Expansion target: semantic IR atoms, not original prose.

## Generativity gate

A novel code-oriented composition was instantiated using `narel` and `vesh` without adding new lexicon definitions. Verified: **yes**.

`narel(codeA,codeB,sortMeaning,developer)` expands to:

```text
ISO(codeA,codeB,sortMeaning);PATH(codeA,sortMeaning,developer,path[codeA]);PATH(codeB,sortMeaning,developer,path[codeB]);DIFF(path[codeA],path[codeB])
```

`vesh(codeA,sortMeaning,computeBoundary)` expands to:

```text
MEAN(codeA,sortMeaning);BOUND(sortMeaning,computeBoundary)
```

## Interpretation boundary

EXP-0001 establishes only that a manually specified finite semantic structure can be hierarchically re-based into shorter reusable lexemes/operators under an explicit dictionary and expansion contract. It does not establish automatic semantic discovery, human comprehension of the new lexemes without learning, or the stronger infinite-space claims in the source papers.
