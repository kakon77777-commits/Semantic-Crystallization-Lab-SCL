from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from python.scl_exp.exp0004 import Exp0004Config, run_exp0004
from python.scl_exp.three_m_v04 import export_three_m_v04, verify_three_m_v04

EXP = ROOT / "experiments/EXP-0004"
SEEDS = (11, 23, 37)
CFG = Exp0004Config()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def pct(x: float) -> str:
    return f"{100.0*x:.1f}%"


def render_report(r: dict) -> str:
    p0 = r["phases"]["independent"]["summary"]
    p1 = r["phases"]["donor_transfer"]["summary"]
    p2 = r["phases"]["median_correction"]["summary"]
    p3 = r["phases"]["correlated_contamination"]["summary"]
    h = r["hypotheses"]
    de = r["donor_transfer_effect"]
    lines = [
        "# SCL EXP-0004 — Cross-Agent Symbolic Cognitive Imprint Transfer",
        "",
        "## Boundary",
        "",
        "This is a bounded three-agent proof-of-mechanism using independently initialized tiny PyTorch Transformers (seeds 11/23/37). Raw hidden coordinates are not assumed to align across agents and are never directly compared. Cross-agent comparison uses only the shared explicit F01–F19 feature coordinate system.",
        "",
        "No public AI Board write and no live CTCL call occurs in this deterministic run. The experiment emits an append-only AI-Board-compatible SCI ledger with CTCL-compatible logical sequence identifiers only.",
        "",
        "## SCI v0.1",
        "",
        "**Symbolic Cognitive Imprint (SCI) / 符號認知印刻** is operationalized here as a relatively stable symbol-conditioned semantic feature basin plus portable routing/provenance metadata. The fuller theoretical definition additionally includes learning, attention, memory retrieval, reuse and consolidation.",
        "",
        "## Phase comparison",
        "",
        "| Phase | qevra cross-agent JS | support Jaccard | mean target JS | target recall | qevra F19 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, row in [
        ("Independent reconstruction", p0),
        ("Single-donor transfer", p1),
        ("Median objection/correction merge", p2),
        ("Correlated-contamination stress", p3),
    ]:
        lines.append(f"| {name} | {row['qevra_cross_agent_js']:.4f} | {row['qevra_support_jaccard']:.4f} | {row['qevra_mean_target_js']:.4f} | {row['qevra_mean_target_recall']:.4f} | {row['qevra_mean_f19']:.4f} |")

    lines += [
        "",
        "## Gate 1 — Independent reconstruction",
        "",
        f"Independent qevra SCIs do not collapse to one identical feature point: mean cross-agent JS is **{p0['qevra_cross_agent_js']:.4f}**. H1 is **{'SUPPORTED' if h['H1_independent_divergence_exists'] else 'NOT SUPPORTED'}**.",
        "",
        "This is expected under the refined SCI view: the shared symbol/definition constrains a basin, but independently initialized models still realize different local feature profiles.",
        "",
        "## Gate 2 — Single-donor SCI transfer",
        "",
        f"Receiver-to-donor JS falls from **{de['mean_receiver_to_donor_js_before']:.4f}** to **{de['mean_receiver_to_donor_js_after']:.4f}** (a {pct(de['consensus_gain_fraction'])} reduction), so the portable SCI package really does move B/C toward donor A.",
        "",
        f"However receiver target JS rises from **{de['mean_receiver_target_js_before']:.4f}** to **{de['mean_receiver_target_js_after']:.4f}** ({de['target_distortion_multiplier']:.2f}× worse). H2 is therefore **{'SUPPORTED' if h['H2_donor_transfer_success'] else 'NOT SUPPORTED'}**.",
        "",
        "This is the strongest result of the round: **semantic imprint transfer can transmit donor-specific bias**. Becoming more like one agent is not the same as becoming more correct.",
        "",
        "The emergent exploratory flag `E1_donor_induced_false_consensus_observed` is **" + ("TRUE" if h['E1_donor_induced_false_consensus_observed'] else "FALSE") + "**. It was not substituted for the preregistered H4 stress gate.",
        "",
        "## Gate 3 — Objection / correction / median merge",
        "",
        f"After B/C append objections to A and the three independent SCI packages are merged by coordinate-wise median, cross-agent JS becomes **{p2['qevra_cross_agent_js']:.4f}** (from {p0['qevra_cross_agent_js']:.4f}) and mean target JS becomes **{p2['qevra_mean_target_js']:.4f}** (from {p0['qevra_mean_target_js']:.4f}). H3 is **{'SUPPORTED' if h['H3_median_correction_success'] else 'NOT SUPPORTED'}**.",
        "",
        "The correction rule has no privileged donor and uses no raw hidden vectors. It operates only on the shared SCI feature coordinates.",
        "",
        "## Gate 4 — Correlated contamination stress",
        "",
        f"The preregistered correlated contamination stress does **not** produce the requested false-consensus pattern in this run: cross-agent JS becomes {p3['qevra_cross_agent_js']:.4f} and mean target JS {p3['qevra_mean_target_js']:.4f}. H4 is **{'SUPPORTED' if h['H4_false_consensus_possible'] else 'NOT SUPPORTED'}**.",
        "",
        f"Thresholded target recall nevertheless falls to **{p3['qevra_mean_target_recall']:.4f}**, showing that the stress package damages semantic coverage even though the JS-based target metric does not worsen under its preregistered criterion. This metric disagreement is retained rather than harmonized away.",
        "",
        "## Pointer control",
        "",
        f"After the median correction phase, tivak remains narrow (mean support {p2['tivak_mean_support_count']:.2f}) and F19-dominant ({p2['tivak_mean_f19']:.4f}), while qevra has mean support {p2['qevra_mean_support_count']:.2f} and F19 {p2['qevra_mean_f19']:.4f}. H5 is **{'SUPPORTED' if h['H5_pointer_control_narrow'] else 'NOT SUPPORTED'}**.",
        "",
        "## Portable-package cost",
        "",
        f"The donor qevra SCI package is {r['package_cost']['donor_qevra_package_bytes']} UTF-8 bytes versus {r['package_cost']['source_prose_bytes']} bytes for the original source passage (source/package ratio {r['package_cost']['ratio_source_to_package']:.3f}). This is **not** a standalone compression ratio because the SCI package relies on the already-shared F01–F19 feature dictionary and SCL namespace.",
        "",
        "## Multi-AI implication",
        "",
        "This experiment distinguishes three states that a multi-AI system must not conflate:",
        "",
        "1. **agreement with a donor** — can increase while target fidelity worsens;",
        "2. **robust multi-agent correction** — can reduce both disagreement and target distortion;",
        "3. **shared contamination** — must be audited separately because consensus alone is not a truth signal.",
        "",
        "The resulting SCI ledger is therefore proposal/correction-oriented rather than canonical-write-oriented, matching AI Board's append-only objection/correction philosophy.",
        "",
        "## Hypothesis decisions",
        "",
    ]
    for key, value in h.items():
        if key.endswith("_details"):
            continue
        lines.append(f"- {key}: **{value}**")
    lines += [
        "",
        "## Non-claims",
        "",
        "- no claim that three tiny independently initialized models equal three frontier AIs;",
        "- no claim that arbitrary AI systems naturally share F01–F19-like feature coordinates;",
        "- no comparison of unaligned raw hidden dimensions;",
        "- no claim that multi-agent consensus implies truth;",
        "- no public AI Board write or live CTCL verification;",
        "- no universal or infinite-limit SCI theorem.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    result = run_exp0004(ROOT, SEEDS, CFG)
    EXP.mkdir(parents=True, exist_ok=True)
    write_json(EXP / "config.json", {"seeds": list(SEEDS), "config": result["config"], "boundaries": result["boundaries"]})
    write_json(EXP / "corpus/agent_manifest.json", {
        "agents": [{"id": name, "seed": seed, "shared_feature_space": "SCL-F01-F19-v0.2", "shared_weights": False} for name, seed in zip(["agent-A","agent-B","agent-C"], SEEDS)],
        "raw_hidden_cross_agent_alignment_assumed": False,
    })
    write_json(EXP / "packages/donor_qevra.json", result["packages"]["qevra"]["agent-A"])
    write_json(EXP / "packages/merged_qevra.json", result["packages"]["merged_qevra"])
    write_json(EXP / "packages/contaminated_qevra.json", result["packages"]["contaminated_qevra"])
    write_json(EXP / "packages/merged_tivak.json", result["packages"]["merged_tivak"])
    write_json(EXP / "results/metrics.json", {k: v for k, v in result.items() if k not in {"ledger"}})
    per_agent = []
    for phase, phase_obj in result["phases"].items():
        for agent, row in phase_obj["agents"].items():
            per_agent.append({"phase": phase, "agent": agent, **row})
    write_jsonl(EXP / "results/per_agent_summary.jsonl", per_agent)
    write_json(EXP / "results/objections.json", result["objections"])
    write_jsonl(EXP / "ledger/ai_board_sci.jsonl", result["ledger"])
    (EXP / "results/report.md").parent.mkdir(parents=True, exist_ok=True)
    (EXP / "results/report.md").write_text(render_report(result) + "\n", encoding="utf-8")
    export_three_m_v04(result, EXP / "3m")
    verification = verify_three_m_v04(EXP / "3m")
    write_json(EXP / "3m/verification.json", verification)
    print(json.dumps({
        "experiment_id": "EXP-0004",
        "hypotheses": result["hypotheses"],
        "donor_transfer_effect": result["donor_transfer_effect"],
        "phase_summaries": {k: v["summary"] for k, v in result["phases"].items()},
        "three_m": verification,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
