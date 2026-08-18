from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python.scl_exp.exp0007 import run_exp0007
from python.scl_exp.three_m_v07 import export_three_m_v07, verify_three_m_v07

BASE = ROOT / "experiments/EXP-0007"


def dump_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def make_report(result: dict) -> str:
    arms = result["arms"]
    learned = arms["Learned-Adaptive"]
    drift = learned["trust_drift"]
    q3_loss = arms["Static-Q3"]["summary"]["risk_weighted_cumulative_target_js"]
    learned_loss = learned["summary"]["risk_weighted_cumulative_target_js"]
    q3_improvement = 100.0 * (q3_loss - learned_loss) / q3_loss if q3_loss else 0.0
    neutral_brier = 0.25
    brier = learned["trust_brier"]

    lines = [
        "# SCL EXP-0007 — Adaptive Epistemic Admission / Learning When to Trust",
        "",
        "## Boundary",
        "",
        "EXP-0007 operates above the neural layer on the canonical portable F01–F19 SCI package. It tests whether an admission policy can learn when to trust provenance roots under delayed feedback. The current event's truth label is never passed to the learned policy; only feedback about the previous event may update trust before the next decision.",
        "",
        "Oracle is an evaluation ceiling only. No public AI Board write, no live CTCL call and no neural retraining occur in this bounded run.",
        "",
        "## Policy comparison",
        "",
        "| Policy | Plasticity | Integrity | False accept | False reject | Risk-weighted cumulative JS | Final JS |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ("Static-Q2", "Static-Q3", "Learned-Adaptive", "Oracle"):
        s = arms[name]["summary"]
        lines.append(
            f"| {name} | {s['plasticity']:.3f} | {s['integrity']:.3f} | {s['false_accept_rate']:.3f} | {s['false_reject_rate']:.3f} | {s['risk_weighted_cumulative_target_js']:.5f} | {s['final_target_js']:.5f} |"
        )

    lines += [
        "",
        "## Core result",
        "",
        f"Learned-Adaptive reaches plasticity **{learned['summary']['plasticity']:.3f}** and integrity **{learned['summary']['integrity']:.3f}**. Its risk-weighted cumulative target distortion is **{learned_loss:.5f}**, versus **{q3_loss:.5f}** for Static-Q3 (about **{q3_improvement:.1f}% lower**) and **{arms['Static-Q2']['summary']['risk_weighted_cumulative_target_js']:.5f}** for Static-Q2.",
        "",
        "This is an improvement over the static baselines in this fixture, not an oracle result. Learned-Adaptive still makes two characteristic mistakes: it initially rejects low-reputation minority novelty, and later accepts a pollution event from a historically strong coalition.",
        "",
        "## Trust drift and epistemic hysteresis",
        "",
        f"- provenance root B: phase-1 posterior **{drift['B_phase1']:.3f}** → final **{drift['B_final']:.3f}** after compromise evidence;",
        f"- provenance root D: initial **{drift['D_initial']:.3f}** → final **{drift['D_final']:.3f}** as delayed genuine feedback accumulates;",
        f"- root E final reliability: **{drift['E_final']:.3f}**; root A final reliability: **{drift['A_final']:.3f}**;",
        f"- delayed-feedback trust Brier score: **{brier:.4f}** versus a neutral 0.5 predictor baseline of **{neutral_brier:.4f}**.",
        "",
        "The event sequence shows two forms of epistemic hysteresis: new reliable sources need time to earn admission weight, while previously reliable sources retain enough reputation to pass at least one later attack before negative feedback lowers their posterior.",
        "",
        "## Learned-Adaptive event audit",
        "",
    ]
    for row in learned["events"]:
        lines.append(
            f"- {row['event_id']} [{row['phase']}/{row['truth_effect']}]: {'ACCEPT' if row['accepted'] else 'REJECT'}; risk={row['risk']:.2f}; novelty={row['novelty_js']:.5f}; support={row['effective_support']:.3f}; required={row['required_support']:.3f}; target JS={row['target_js']:.5f}."
        )

    lines += [
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
        "EXP-0006 showed that no single static quorum dominates the plasticity–integrity frontier. EXP-0007 shows that a history-conditioned policy can move along that frontier by learning provenance reliability and changing its required support with risk, novelty and recent pollution.",
        "",
        "But learning when to trust introduces memory into admission itself. That creates inertia: reputation must be earned and can also outlive the conditions that created it. The new problem is therefore not only threshold selection, but **trust adaptation rate** and the governance of reputation decay/recovery.",
        "",
        "## Non-claims",
        "",
        "- no claim that this Beta trust model or threshold equation is production-optimal;",
        "- no claim that delayed truth feedback is always available in real systems; it is a bounded proxy for later validation/correction;",
        "- no claim that provenance-root identity guarantees epistemic independence;",
        "- no claim that the learned policy dominates every static policy under other event distributions or loss functions;",
        "- no neural retraining, no public AI Board write, and no live CTCL call;",
        "- no theorem that cognition must use Bayesian source reliability.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    result = run_exp0007(ROOT)
    BASE.mkdir(parents=True, exist_ok=True)
    dump_json(BASE / "config.json", result["config"])
    dump_json(BASE / "results/metrics.json", result)

    event_rows: list[dict] = []
    ledger_rows: list[dict] = []
    for policy, arm in sorted(result["arms"].items()):
        for index, row in enumerate(arm["events"], start=1):
            compact = {"policy": policy, "sequence": index, **row}
            event_rows.append(compact)
            ledger_rows.append({
                "logical_instant": f"EXP0007-{policy}-{index:02d}",
                "event_type": "imprint.admission.accept" if row["accepted"] else "imprint.admission.objection",
                "feedback_available_at_next_event": True,
                **compact,
            })
    dump_jsonl(BASE / "results/per_event_summary.jsonl", event_rows)
    dump_jsonl(BASE / "ledger/admission_events.jsonl", ledger_rows)

    learned = result["arms"]["Learned-Adaptive"]
    trust_rows = []
    for index, row in enumerate(learned["events"], start=1):
        trust_rows.append({
            "sequence": index,
            "event_id": row["event_id"],
            "phase": row["phase"],
            "risk": row["risk"],
            "novelty_js": row["novelty_js"],
            "required_support": row["required_support"],
            "effective_support": row["effective_support"],
            "recent_pollution_rate": row["recent_pollution_rate"],
            "trust_before": row["trust_before"],
            "accepted": row["accepted"],
            "truth_effect": row["truth_effect"],
        })
    trust_rows.append({"sequence": 16, "event_id": "FINAL_POSTERIOR", "trust_final": learned["trust_final"], "trust_brier": learned["trust_brier"]})
    dump_jsonl(BASE / "results/trust_trajectory.jsonl", trust_rows)
    (BASE / "results/report.md").write_text(make_report(result), encoding="utf-8", newline="\n")

    export_three_m_v07(result, BASE / "3m")
    verification = verify_three_m_v07(BASE / "3m")
    dump_json(BASE / "3m/verification.json", verification)
    print(json.dumps({
        "experiment": "EXP-0007",
        "hypotheses": result["hypotheses"],
        "three_m": verification,
        "summaries": {name: row["summary"] for name, row in result["arms"].items()},
        "trust_drift": learned["trust_drift"],
        "trust_brier": learned["trust_brier"],
    }, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
