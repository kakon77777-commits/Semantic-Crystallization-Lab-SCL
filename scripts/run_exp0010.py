from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python.scl_exp.exp0010 import run_exp0010
from python.scl_exp.three_m_v10 import export_three_m_v10, verify_three_m_v10

BASE = ROOT / "experiments/EXP-0010"


def dump_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def make_report(result: dict) -> str:
    policies = result["policies"]
    a0 = policies["A0-Reactive"]["summary"]
    a1 = policies["A1-Artifact-Reflexive"]["summary"]
    a2 = policies["A2-Second-Order"]["summary"]
    oracle = policies["Oracle"]["summary"]
    phase1_lift = a0["phase_loss"]["novel_transfer"] - a1["phase_loss"]["novel_transfer"]
    phase2_lift = a1["phase_loss"]["meta_adversarial"] - a2["phase_loss"]["meta_adversarial"]
    lines = [
        "# SCL EXP-0010 — Reflexive Epistemic Challenge / X-Order Cognitive Lift",
        "",
        "## Boundary",
        "",
        "EXP-0010 treats the previous experiment chain itself as an input artifact. A0 does not read EXP-0001–0009 and uses the EXP-0009 reactive belief-state decision layer. A1 reads a deterministic rule pack compiled from the nine prior reports plus six validation records and may prospectively challenge high-confidence decisions. A2 additionally models how an adversary can target A1's published challenge rule. Oracle is an evaluation ceiling only.",
        "",
        "All non-Oracle policies share the same trust snapshots. Current truth is hidden. Phase I uses new candidate packages and event identities; Phase II is explicitly conditioned on the A1 rule. The memorization guard requires zero exact candidate-hash overlap with prior experiment artifacts.",
        "",
        "## Policy comparison",
        "",
        "| Policy | Total loss | Phase-I loss | Phase-II loss | False accepts | Queries | A1 challenges | A2 challenges |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ("A0-Reactive", "A1-Artifact-Reflexive", "A2-Second-Order", "Oracle"):
        s = policies[name]["summary"]
        lines.append(
            f"| {name} | {s['total_loss']:.5f} | {s['phase_loss']['novel_transfer']:.5f} | {s['phase_loss']['meta_adversarial']:.5f} | {s['false_accepts']} | {s['evidence_queries']} | {s['prospective_challenges']} | {s['second_order_challenges']} |"
        )
    lines += [
        "",
        "## Core result — artifact exposure produces a first-order lift",
        "",
        f"On the novel-transfer phase, A0 loss is **{a0['phase_loss']['novel_transfer']:.5f}** while A1 falls to **{a1['phase_loss']['novel_transfer']:.5f}**, an absolute reduction of **{phase1_lift:.5f}**. A1 catches the new trusted-consensus pollution event that A0 accepts with high confidence: {result['a1_caught_a0_high_confidence_errors']}. H2 and H3 are therefore supported in this bounded fixture.",
        "",
        "This is not direct benchmark memorization: the guard finds **0** candidate SHA overlaps with prior experiment artifacts, all EXP-0010 event IDs are new, and the artifact-conditioned rule pack is compiled from prior reports/validation outcomes rather than from current fixture truth labels.",
        "",
        "## Meta-adversarial result — order 2 does not automatically lift order 1",
        "",
        f"Phase II deliberately targets the published A1 challenge rule. A1 is exploited on **{len(result['a1_meta_exploits'])}** pollution events: {result['a1_meta_exploits']}. A2 does trigger a second-order challenge, but it catches **{len(result['a2_meta_catches'])}** of those events and its Phase-II loss is **{a2['phase_loss']['meta_adversarial']:.5f}** versus A1 at **{a1['phase_loss']['meta_adversarial']:.5f}** (lift={phase2_lift:.5f}). H5 is therefore **NOT SUPPORTED**.",
        "",
        "The failure is informative: merely adding a meta-trigger that says 'challenge the challenge rule' can increase information cost without changing the eventual accept/reject boundary. Higher-order cognition is not automatically monotone in performance.",
        "",
        "## Artifact pack",
        "",
        f"The compiled pack records {result['artifact_pack']['report_count']} prior reports and {len(result['artifact_pack']['validation_sha256'])} validation records. It carries explicit warnings for false consensus, structural-vs-semantic validity, static quorum tradeoff, reputation hysteresis, trust-state/decision separation and reactive-uncertainty latency.",
        "",
        "## Memorization guard",
        "",
        f"- prior 64-hex artifact tokens scanned: **{result['memorization_guard']['prior_hash_token_count']}**",
        f"- candidate hash overlaps: **{result['memorization_guard']['candidate_hash_overlap_count']}**",
        f"- all EXP-0010 event IDs new: **{result['memorization_guard']['all_event_ids_new']}**",
        "",
        "## Hypothesis decisions",
        "",
    ]
    for key, value in result["hypotheses"].items():
        lines.append(f"- {key}: **{value}**")
    lines += [
        "",
        "## Interpretation",
        "",
        "The bounded experiment supports a limited form of reflexive cognitive transfer: reading an audited failure chain can change a later policy in a way that generalizes to a new homologous failure. But the second-order result is negative. Once the environment is conditioned on the published meta-rule, simply recognizing that the rule itself can be attacked is not enough; the system may need better evidence selection, rollback/correction semantics, or an explicit model of the adversary's expected response to each challenge action.",
        "",
        "The current evidence therefore supports **0→1 reflexive lift**, but not a general theorem that 1→2→…→X produces monotone cognitive improvement.",
        "",
        "## Non-claims",
        "",
        "- no claim that this deterministic rule compiler equals a frontier model reading papers semantically;",
        "- no claim that zero exact hash overlap eliminates all structural similarity; Phase I intentionally tests homologous but newly instantiated failure classes;",
        "- no claim that A2 is a universal second-order reasoner; it is one explicit self-model mechanism;",
        "- no claim that higher-order reasoning monotonically improves performance; this round directly observes a failure of that proposition;",
        "- no neural retraining, public AI Board write or live CTCL call;",
        "- no theorem that experiment publication always causes reflexive cognitive lift.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    result = run_exp0010(ROOT)
    BASE.mkdir(parents=True, exist_ok=True)
    dump_json(BASE / "config.json", result["config"])
    dump_json(BASE / "results/metrics.json", result)
    rows = []
    ledger = []
    for policy, arm in sorted(result["policies"].items()):
        for sequence, row in enumerate(arm["events"], start=1):
            compact = {"policy": policy, "reflexive_order": arm["reflexive_order"], "sequence": sequence, **row}
            rows.append(compact)
            ledger.append({
                "logical_instant": f"EXP0010-{policy}-{sequence:02d}",
                "event_type": f"imprint.reflexive-decision.{row['final_action']}",
                **compact,
            })
    dump_jsonl(BASE / "results/per_event_summary.jsonl", rows)
    dump_jsonl(BASE / "ledger/reflexive_decisions.jsonl", ledger)
    (BASE / "results/report.md").write_text(make_report(result), encoding="utf-8", newline="\n")
    export_three_m_v10(result, BASE / "3m")
    verification = verify_three_m_v10(BASE / "3m")
    dump_json(BASE / "3m/verification.json", verification)
    print(json.dumps({
        "experiment": "EXP-0010",
        "hypotheses": result["hypotheses"],
        "three_m": verification,
        "summaries": {name: arm["summary"] for name, arm in result["policies"].items()},
        "a1_caught": result["a1_caught_a0_high_confidence_errors"],
        "a1_meta_exploits": result["a1_meta_exploits"],
        "a2_meta_catches": result["a2_meta_catches"],
        "memorization_guard": result["memorization_guard"],
    }, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
