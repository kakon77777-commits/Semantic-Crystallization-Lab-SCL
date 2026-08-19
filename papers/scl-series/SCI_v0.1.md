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

SCL EXP-0001 through EXP-0010 provide finite engineering demonstrations only. They do not prove universal semantic fixed points, cross-model ontology equivalence, or the stronger cardinality/ontological conjectures in the source theory papers.

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

## Adaptive epistemic admission note

EXP-0007 treats admission itself as a learned, history-conditioned process. A structurally valid transition is evaluated using provenance-root reliability estimated from delayed validation feedback, together with current risk, semantic novelty and recent pollution prevalence.

Operationally, this adds a fourth distinction:

$$
\text{Admissibility threshold} \neq \text{fixed quorum}.
$$

A learned threshold can move along the plasticity–integrity frontier, but it introduces **epistemic hysteresis**: new reliable sources may be under-trusted until enough feedback arrives, while previously reliable sources may retain excess trust after compromise. This is a bounded observation about the EXP-0007 benchmark, not a claim that Beta reputation or any specific trust update rule is universally correct.

## Trust-dynamics note

EXP-0008 separates the quality of an internal trust state from the quality of the downstream admission decision. Three policies share one admission equation while differing only in how historical source evidence is retained: cumulative memory, fixed exponential decay, or volatility-sensitive adaptive decay/recovery.

The bounded result shows that a more finely calibrated trust state can still be decision-equivalent to a simpler history if both remain on the same side of the hard admission threshold. SCI governance therefore may need to represent trust uncertainty/volatility directly rather than compressing all trust history to one scalar support score.

This is an experimental warning, not a claim that fixed decay is universally optimal.

## Uncertainty-aware decision note

EXP-0009 holds the learned trust trajectory fixed and varies only the decision projection. This yields a fifth operational distinction:

$$
\text{Belief-state richness} \neq \text{decision quality}.
$$

Posterior uncertainty, volatility and disagreement can justify `Seek Evidence` or `Defer`, but reactive use of those signals does not guarantee lower total loss. In the bounded benchmark, Belief-State reduces high-risk false accepts while losing overall after the first historically trusted coalition attack passes before negative feedback exists. This motivates a prospective challenge rule: sufficiently high risk/novelty may warrant independent evidence even when current confidence is high.

## Reflexive artifact note

EXP-0010 treats the prior experiment chain itself as a cognition-shaping artifact. A deterministic rule pack is compiled from the previous reports and validation records, then evaluated on newly instantiated candidate packages with an explicit zero exact-hash-overlap guard. This adds a sixth operational distinction:

$$
\text{experiment result as description} \neq \text{experiment artifact as future cognitive input}.
$$

In the bounded fixture, first-order artifact exposure produces a large transfer gain on a new homologous failure class, while a second-order policy that models attacks against the first-order challenge rule does **not** improve further. The result therefore supports a limited `0→1` reflexive lift but rejects any simple monotonic law of the form

$$
\text{higher reflexive order} \Rightarrow \text{higher decision quality}.
$$

This is not evidence that a frontier AI will necessarily acquire the same meta-strategies merely by reading the repository. It is a finite engineering demonstration that an experiment artifact can be made causally active in a later decision policy, and that the resulting meta-policy itself becomes part of the next adversarial environment.
