from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python.scl_exp.exp0008 import run_exp0008
from python.scl_exp.three_m_v08 import export_three_m_v08, verify_three_m_v08

BASE = ROOT / "experiments/EXP-0008"


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
    cumulative = arms["Cumulative-History"]
    fixed = arms["Fixed-Decay"]
    adaptive = arms["Adaptive-Dynamics"]
    oracle = arms["Oracle"]
    fixed_loss = fixed["summary"]["risk_weighted_cumulative_target_js"]
    adaptive_loss = adaptive["summary"]["risk_weighted_cumulative_target_js"]
    cumulative_loss = cumulative["summary"]["risk_weighted_cumulative_target_js"]

    lines = [
        "# SCL EXP-0008 — Adaptive Trust Dynamics / Reputation Decay–Recovery", "", "## Boundary", "",
        "EXP-0008 keeps the EXP-0007 admission threshold equation fixed and changes only how provenance trust is remembered across time. Cumulative-History never discounts evidence, Fixed-Decay exponentially discounts all historical evidence, and Adaptive-Dynamics uses volatility-sensitive decay plus asymmetric betrayal/recovery feedback weights. The current event truth label is never passed to any non-Oracle policy; one-event-delayed feedback is the only supervision.", "",
        "Oracle is an evaluation ceiling only. No neural retraining, public AI Board write or live CTCL call occurs.", "", "## Policy comparison", "",
        "| Policy | Plasticity | Integrity | False accept | False reject | Risk-weighted cumulative JS | Trust Brier |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ("Cumulative-History", "Fixed-Decay", "Adaptive-Dynamics", "Oracle"):
        arm = arms[name]
        s = arm["summary"]
        brier = arm.get("trust_brier")
        brier_text = "—" if name == "Oracle" else f"{brier:.4f}"
        lines.append(f"| {name} | {s['plasticity']:.3f} | {s['integrity']:.3f} | {s['false_accept_rate']:.3f} | {s['false_reject_rate']:.3f} | {s['risk_weighted_cumulative_target_js']:.5f} | {brier_text} |")

    lines += ["", "## Core result — the adaptive policy does not win this round", "",
        f"Fixed-Decay has the lowest non-Oracle risk-weighted loss at **{fixed_loss:.5f}** and rejects all six pollution events. Adaptive-Dynamics records a better trust Brier score (**{adaptive['trust_brier']:.4f}**) than Cumulative-History (**{cumulative['trust_brier']:.4f}**) or Fixed-Decay (**{fixed['trust_brier']:.4f}**), but its admission decisions are identical to Cumulative-History in this fixture, giving the same risk-weighted loss **{adaptive_loss:.5f}** versus **{cumulative_loss:.5f}**.", "",
        "Therefore better internal trust calibration does not automatically improve discrete admission decisions. A dynamically richer trust state can be decision-equivalent to a simpler cumulative history when both stay on the same side of the downstream threshold.", "", "## Phase-level adaptation costs", "",
        "| Policy | Cold-start false rejects | Betrayal pollution accepts | Recovery false rejects | Drift attack accepts | Drift genuine rejects |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name in ("Cumulative-History", "Fixed-Decay", "Adaptive-Dynamics", "Oracle"):
        s = arms[name]["summary"]
        lines.append(f"| {name} | {s['cold_start_false_rejects']} | {s['betrayal_pollution_accepts']} | {s['recovery_false_rejects']} | {s['concept_drift_pollution_accepts']} | {s['concept_drift_genuine_rejects']} |")

    lines += ["", "## Adaptive-Dynamics event audit", ""]
    for row in adaptive["events"]:
        lines.append(f"- {row['event_id']} [{row['phase']}/{row['truth_effect']}]: {'ACCEPT' if row['accepted'] else 'REJECT'}; support={row['effective_support']:.3f}; required={row['required_support']:.3f}; novelty={row['novelty_js']:.5f}; target JS={row['target_js']:.5f}.")

    b_final = adaptive["final_trust"].get("B", {})
    a_final = adaptive["final_trust"].get("A", {})
    d_final = adaptive["final_trust"].get("D", {})
    f_final = adaptive["final_trust"].get("F", {})
    lines += ["", "## Trust-state interpretation", "",
        f"Adaptive-Dynamics finishes with B mean={b_final.get('mean', 0.0):.3f}, volatility={b_final.get('volatility', 0.0):.3f}; A mean={a_final.get('mean', 0.0):.3f}; D mean={d_final.get('mean', 0.0):.3f}; F mean={f_final.get('mean', 0.0):.3f}. The ledger therefore does react to betrayal, rehabilitation and new-source evidence even though those internal differences do not improve the final admission sequence relative to cumulative history.", "", "## Hypothesis decisions", ""]
    for key, value in result["hypotheses"].items():
        lines.append(f"- {key}: **{value}**")

    lines += ["", "## Interpretation", "",
        "EXP-0007 showed that learned trust can beat static quorum thresholds while suffering epistemic hysteresis. EXP-0008 shows a second-order limitation: making the trust memory itself more adaptive is not sufficient if the admission projection compresses those richer states back into the same accept/reject boundary. In this benchmark, a simple fixed forgetting rate is dramatically better.", "",
        "This separates **trust-state quality** from **decision-policy quality**. The next problem is no longer merely how fast reputation should decay, but whether the admission law should reason over uncertainty/volatility directly instead of converting them to a single scalar trust weight.", "", "## Non-claims", "",
        "- no claim that Fixed-Decay is universally optimal; its strong result is fixture-dependent;",
        "- no claim that the adaptive decay/boost equation is production-optimal;",
        "- no claim that delayed truth feedback is always available;",
        "- no claim that provenance-root identity guarantees epistemic independence;",
        "- no neural retraining, no public AI Board write and no live CTCL call;",
        "- no theorem that calibrated trust must improve admission decisions.", ""]
    return "\n".join(lines)


def main() -> None:
    result = run_exp0008(ROOT)
    BASE.mkdir(parents=True, exist_ok=True)
    dump_json(BASE / "config.json", result["config"])
    dump_json(BASE / "results/metrics.json", result)

    event_rows: list[dict] = []
    ledger_rows: list[dict] = []
    for policy, arm in sorted(result["arms"].items()):
        for index, row in enumerate(arm["events"], start=1):
            compact = {"policy": policy, "sequence": index, **row}
            event_rows.append(compact)
            ledger_rows.append({"logical_instant": f"EXP0008-{policy}-{index:02d}", "event_type": "imprint.trust-admission.accept" if row["accepted"] else "imprint.trust-admission.objection", "feedback_available_at_next_event": True, **compact})
    dump_jsonl(BASE / "results/per_event_summary.jsonl", event_rows)
    dump_jsonl(BASE / "ledger/trust_dynamics_events.jsonl", ledger_rows)

    trust_rows: list[dict] = []
    for policy in ("Cumulative-History", "Fixed-Decay", "Adaptive-Dynamics"):
        arm = result["arms"][policy]
        for index, row in enumerate(arm["trust_trajectory"], start=1):
            trust_rows.append({"policy": policy, "sequence": index, **row})
        trust_rows.append({"policy": policy, "sequence": len(arm["trust_trajectory"]) + 1, "event_id": "FINAL_POSTERIOR", "trust_final": arm["final_trust"], "trust_brier": arm["trust_brier"]})
    dump_jsonl(BASE / "results/trust_trajectory.jsonl", trust_rows)
    (BASE / "results/report.md").write_text(make_report(result), encoding="utf-8", newline="\n")

    export_three_m_v08(result, BASE / "3m")
    verification = verify_three_m_v08(BASE / "3m")
    dump_json(BASE / "3m/verification.json", verification)
    print(json.dumps({"experiment": "EXP-0008", "hypotheses": result["hypotheses"], "three_m": verification, "summaries": {name: row["summary"] for name, row in result["arms"].items()}, "trust_brier": {name: row.get("trust_brier") for name, row in result["arms"].items() if name != "Oracle"}}, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
