# SCL EXP-0005 — Protocol–Persistent Cognition Continuity

## Boundary

EXP-0005 isolates continuity mechanics above the neural layer. It consumes the canonical portable F01–F19 SCI artifacts produced by EXP-0004 and performs no new neural training. Cross-agent comparison therefore remains in the explicit shared feature coordinate only.

No public AI Board write and no live CTCL call occurs. The exported ledger is append-only AI-Board-compatible, while logical instants are deterministic CTCL-compatible labels rather than verified wall-clock instants.

## 2×2 factorial result

| Arm | Protocol | Persistence | Restart JS | Pre-bootstrap correction retention | Final correction retention | Final target JS | Final cross-agent JS |
|---|---|---|---:|---:|---:|---:|---:|
| A00 | no | no | 0.0243 | 0.00 | 0.00 | 0.1053 | 0.0000 |
| A01 | no | yes | 0.0000 | 1.00 | 0.00 | 0.1053 | 0.0000 |
| A10 | yes | no | 0.0243 | 0.00 | 1.00 | 0.0251 | 0.0000 |
| A11 | yes | yes | 0.0000 | 1.00 | 1.00 | 0.0251 | 0.0000 |

## Factor interpretation

Persistence isolates restart continuity: the non-persistent arms have mean immediate restart JS **0.0243**, while the persistent arms are **0.0000**. Persistence therefore preserves the accepted SCI across restart before any external resynchronization.

Protocol isolates correction integrity under hostile or stale traffic: no-protocol arms finish with correction retention **0%**, while protocol arms finish at **100%**.

The factors are therefore orthogonal in this bounded construction:

- persistence answers **what survives inside the agent across time**;
- protocol answers **what the agent is allowed to accept from other agents after restart**.

## A01 — persistence without protocol

A01 restarts with the accepted correction intact (pre-bootstrap retention 1.00 and restart JS 0), but deterministic untyped last-write-wins traffic later overwrites it. Final correction retention is 0.00. This directly supports the claim that persistence alone does not protect a cognition state from semantic overwrite.

## A10 — protocol without persistence

A10 initially loses the accepted SCI at restart (pre-bootstrap retention 0.00; restart JS 0.0243) but recovers it through a valid typed bootstrap and retains it through all subsequent faults. Protocol can therefore restore inter-agent continuity without eliminating the intra-agent restart discontinuity itself.

## A11 — protocol plus persistence

A11 has both immediate restart continuity (restart JS 0) and final correction retention 1.00. In this experiment it is the only arm that needs neither reconstruction after restart nor recovery from semantic overwrite.

## Fault audit

Each protocol arm receives the same four fault classes for all three agents. The fail-closed rejection totals are:

- `conflicting_correction`: **6** rejections
- `missing_provenance`: **3** rejections
- `rollback_to_superseded`: **3** rejections
- `stale_version`: **3** rejections

The conflict count is six because each of three agents receives two competing corrections with the same next version and parent; the protocol quarantines the whole fork rather than accepting the first arrival.

## False-consensus result

The accepted median SCI has target JS **0.0251**. The final no-protocol state has target JS **0.1053**, or **4.19×** the reference distortion, while final cross-agent JS is exactly **0.0000** because every agent converges to the same contaminated last write.

Thus the temporal version of the EXP-0004 warning is explicit:

$$
\text{persistent agreement} \not\Rightarrow \text{persistent truth}
$$

Protocol protects the lineage of a correction; persistence protects the continuity of a cognition state. Neither metric should be replaced by consensus alone.

## Hypothesis decisions

- H1_persistence_reduces_restart_drift: **True**
- H2_protocol_preserves_correction_under_faults: **True**
- H3_joint_protocol_persistence_dominates_continuity: **True**
- H4_persistence_alone_insufficient_against_overwrite: **True**
- H5_protocol_alone_recovers_but_restart_discontinuity_remains: **True**
- H6_consensus_is_not_truth_signal: **True**

## Refined continuity model

The bounded result motivates treating multi-agent cognition as two coupled continuity laws:

$$
\text{Protocol} \approx \text{inter-agent continuity},
$$

$$
\text{Persistence} \approx \text{intra-agent continuity through time}.
$$

Their conjunction is a candidate mechanism for persistent shared cognition, but this experiment does not claim a universal theorem.

## Non-claims

- no new neural generalization claim; EXP-0005 operates on canonical EXP-0004 SCI packages;
- no claim that the median package is universal truth; it is the experiment's accepted correction reference;
- no claim that arbitrary production agents share F01–F19 coordinates;
- no public AI Board write and no live CTCL verification;
- no claim that protocol eliminates malicious authorized updates; this test covers explicit stale/provenance/rollback/fork faults;
- no infinite-time cognition-continuity theorem.
