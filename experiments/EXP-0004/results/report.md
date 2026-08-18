# SCL EXP-0004 — Cross-Agent Symbolic Cognitive Imprint Transfer

## Boundary

This is a bounded three-agent proof-of-mechanism using independently initialized tiny PyTorch Transformers (seeds 11/23/37). Raw hidden coordinates are not assumed to align across agents and are never directly compared. Cross-agent comparison uses only the shared explicit F01–F19 feature coordinate system.

No public AI Board write and no live CTCL call occurs in this deterministic run. The experiment emits an append-only AI-Board-compatible SCI ledger with CTCL-compatible logical sequence identifiers only.

## SCI v0.1

**Symbolic Cognitive Imprint (SCI) / 符號認知印刻** is operationalized here as a relatively stable symbol-conditioned semantic feature basin plus portable routing/provenance metadata. The fuller theoretical definition additionally includes learning, attention, memory retrieval, reuse and consolidation.

## Phase comparison

| Phase | qevra cross-agent JS | support Jaccard | mean target JS | target recall | qevra F19 |
|---|---:|---:|---:|---:|---:|
| Independent reconstruction | 0.0559 | 0.5172 | 0.0526 | 0.7037 | 0.0042 |
| Single-donor transfer | 0.0542 | 0.4167 | 0.0847 | 0.3889 | 0.0035 |
| Median objection/correction merge | 0.0424 | 0.4806 | 0.0400 | 0.6296 | 0.0014 |
| Correlated-contamination stress | 0.0865 | 0.3663 | 0.0524 | 0.5185 | 0.0483 |

## Gate 1 — Independent reconstruction

Independent qevra SCIs do not collapse to one identical feature point: mean cross-agent JS is **0.0559**. H1 is **SUPPORTED**.

## Gate 2 — Single-donor SCI transfer

Receiver-to-donor JS falls from **0.0710** to **0.0438** (a 38.3% reduction), so the portable SCI package really does move B/C toward donor A.

However receiver target JS rises from **0.0268** to **0.0749** (2.80× worse). H2 is therefore **NOT SUPPORTED**.

This is the strongest result of the round: **semantic imprint transfer can transmit donor-specific bias**. Becoming more like one agent is not the same as becoming more correct.

The emergent exploratory flag `E1_donor_induced_false_consensus_observed` is **TRUE**. It was not substituted for the preregistered H4 stress gate.

## Gate 3 — Objection / correction / median merge

After B/C append objections to A and the three independent SCI packages are merged by coordinate-wise median, cross-agent JS becomes **0.0424** (from 0.0559) and mean target JS becomes **0.0400** (from 0.0526). H3 is **SUPPORTED**.

The correction rule has no privileged donor and uses no raw hidden vectors. It operates only on the shared SCI feature coordinates.

## Gate 4 — Correlated contamination stress

The preregistered correlated contamination stress does **not** produce the requested false-consensus pattern in this run: cross-agent JS becomes 0.0865 and mean target JS 0.0524. H4 is **NOT SUPPORTED**.

Thresholded target recall nevertheless falls to **0.5185**, showing that the stress package damages semantic coverage even though the JS-based target metric does not worsen under its preregistered criterion. This metric disagreement is retained rather than harmonized away.

## Pointer control

After the median correction phase, tivak remains narrow (mean support 1.00) and F19-dominant (0.6451), while qevra has mean support 11.33 and F19 0.0014. H5 is **SUPPORTED**.

## Portable-package cost

The donor qevra SCI package is 786 UTF-8 bytes versus 1027 bytes for the original source passage (source/package ratio 1.307). This is **not** a standalone compression ratio because the SCI package relies on the already-shared F01–F19 feature dictionary and SCL namespace.

## Multi-AI implication

This experiment distinguishes three states that a multi-AI system must not conflate:

1. **agreement with a donor** — can increase while target fidelity worsens;
2. **robust multi-agent correction** — can reduce both disagreement and target distortion;
3. **shared contamination** — must be audited separately because consensus alone is not a truth signal.

The resulting SCI ledger is therefore proposal/correction-oriented rather than canonical-write-oriented, matching AI Board's append-only objection/correction philosophy.

## Hypothesis decisions

- H1_independent_divergence_exists: **True**
- H2_donor_transfer_success: **False**
- H3_median_correction_success: **True**
- H4_false_consensus_possible: **False**
- H5_pointer_control_narrow: **True**
- E1_donor_induced_false_consensus_observed: **True**

## Non-claims

- no claim that three tiny independently initialized models equal three frontier AIs;
- no claim that arbitrary AI systems naturally share F01–F19-like feature coordinates;
- no comparison of unaligned raw hidden dimensions;
- no claim that multi-agent consensus implies truth;
- no public AI Board write or live CTCL verification;
- no universal or infinite-limit SCI theorem.
