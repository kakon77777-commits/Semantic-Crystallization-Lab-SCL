# Symbolic Cognitive Imprint (SCI) v0.1

## 中文名稱

**符號認知印刻**

## Core definition

**Symbolic Cognitive Imprint (SCI)** is a relatively stable symbol-conditioned semantic feature basin and routing bias formed through learning, attention, memory retrieval, reuse, and consolidation.

This definition uses *imprint* to mean a persistent but revisable bias/structure. It does not mean an immutable hard-coded belief.

## Bounded operational form used by SCL

For a symbol $s$, model/agent $a$, and compatible context family $C$, let

$$
F_a(s,c) \in [0,1]^m
$$

be the auditable semantic-feature signature in a declared coordinate system. The bounded SCI basin is the context-conditioned family

$$
\mathcal B_a(s)=\{F_a(s,c):c\in C\}.
$$

Its centroid is

$$
\mu_a(s)=\frac{1}{|C|}\sum_{c\in C}F_a(s,c),
$$

while stability is measured by within-basin dispersion and support agreement. Cross-agent SCI comparison is permitted only after defining a shared feature coordinate or an explicit projection between feature spaces.

## Important separation

$$
\text{memory assistance} \neq \text{intrinsic imprint consolidation}.
$$

External retrieval may improve a current inference without changing the symbol-conditioned intrinsic basin. Consolidation means that part of the retrieved/reused structure becomes recoverable from the symbol through the agent's own learned representation/routing.

## Cross-agent form

For agents $a,b$ with different raw hidden spaces, SCI does **not** assume

$$
h_a(s) \cong h_b(s).
$$

Instead, a portable SCI package uses an explicit common feature coordinate $\Phi$:

$$
\Pi_{a\rightarrow\Phi}(\mathcal B_a(s))
\leftrightarrow
\operatorname{SCI}(s)
\leftrightarrow
\Pi_{\Phi\rightarrow b}(\mathcal B_b(s)).
$$

Thus SCI is proposed as a candidate semantic interchange layer, not as proof that internal neural axes are universal.

## Governance principle

An SCI package is a proposal, not truth. In multi-agent use it should support append-only objection, correction, merge and supersession rather than silent overwrite.

## Current evidence boundary

SCL EXP-0001 through EXP-0006 provide finite engineering demonstrations only. They do not prove universal semantic fixed points, cross-model ontology equivalence, or the stronger cardinality/ontological conjectures in the source theory papers.

## Continuity note

EXP-0005 separates two mechanisms that can stabilize an SCI across a multi-agent system:

$$
\text{Protocol} \approx \text{inter-agent continuity},
$$

$$
\text{Persistence} \approx \text{intra-agent continuity through time}.
$$

This is an operational distinction, not an identity theorem. Protocol constrains admissible inter-agent state transitions; persistence preserves an agent's accepted imprint/history across restart. The bounded experiment shows that either factor alone can fail in a different way.

## Transition admissibility note

EXP-0006 adds a third operational distinction beyond protocol and persistence:

$$
\text{Structural transition validity} \neq \text{semantic transition admissibility}.
$$

A persistent SCI must be revisable, but unrestricted revisability allows structurally valid contamination. The bounded experiment therefore treats admissibility as a plasticity–integrity tradeoff: stronger evidence quorums improve resistance to correlated updates while increasing the risk of rejecting genuine minority novelty. This is an experimental decomposition, not a universal optimality theorem.
