from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python.scl_exp.exp0005 import ARM_FACTORS, Exp0005Config, run_exp0005
from python.scl_exp.three_m_v05 import export_three_m_v05, verify_three_m_v05


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def render_report(result: dict) -> str:
    arms = result["arms"]
    ref = result["reference"]
    h = result["hypotheses"]
    false_consensus_ratio = arms["A00"]["summary"]["mean_final_target_js"] / ref["accepted_target_js"]
    lines = [
        "# SCL EXP-0005 — Protocol–Persistent Cognition Continuity",
        "",
        "## Boundary",
        "",
        "EXP-0005 isolates continuity mechanics above the neural layer. It consumes the canonical portable F01–F19 SCI artifacts produced by EXP-0004 and performs no new neural training. Cross-agent comparison therefore remains in the explicit shared feature coordinate only.",
        "",
        "No public AI Board write and no live CTCL call occurs. The exported ledger is append-only AI-Board-compatible, while logical instants are deterministic CTCL-compatible labels rather than verified wall-clock instants.",
        "",
        "## 2×2 factorial result",
        "",
        "| Arm | Protocol | Persistence | Restart JS | Pre-bootstrap correction retention | Final correction retention | Final target JS | Final cross-agent JS |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for arm in ("A00", "A01", "A10", "A11"):
        s = arms[arm]["summary"]
        lines.append(
            f"| {arm} | {'yes' if s['protocol'] else 'no'} | {'yes' if s['persistence'] else 'no'} | "
            f"{s['mean_restart_js']:.4f} | {s['prebootstrap_correction_retention']:.2f} | "
            f"{s['final_correction_retention']:.2f} | {s['mean_final_target_js']:.4f} | {s['final_cross_agent_js']:.4f} |"
        )

    lines += [
        "",
        "## Factor interpretation",
        "",
        f"Persistence isolates restart continuity: the non-persistent arms have mean immediate restart JS **{arms['A00']['summary']['mean_restart_js']:.4f}**, while the persistent arms are **{arms['A01']['summary']['mean_restart_js']:.4f}**. Persistence therefore preserves the accepted SCI across restart before any external resynchronization.",
        "",
        f"Protocol isolates correction integrity under hostile or stale traffic: no-protocol arms finish with correction retention **{arms['A00']['summary']['final_correction_retention']:.0%}**, while protocol arms finish at **{arms['A10']['summary']['final_correction_retention']:.0%}**.",
        "",
        "The factors are therefore orthogonal in this bounded construction:",
        "",
        "- persistence answers **what survives inside the agent across time**;",
        "- protocol answers **what the agent is allowed to accept from other agents after restart**.",
        "",
        "## A01 — persistence without protocol",
        "",
        "A01 restarts with the accepted correction intact (pre-bootstrap retention 1.00 and restart JS 0), but deterministic untyped last-write-wins traffic later overwrites it. Final correction retention is 0.00. This directly supports the claim that persistence alone does not protect a cognition state from semantic overwrite.",
        "",
        "## A10 — protocol without persistence",
        "",
        f"A10 initially loses the accepted SCI at restart (pre-bootstrap retention 0.00; restart JS {arms['A10']['summary']['mean_restart_js']:.4f}) but recovers it through a valid typed bootstrap and retains it through all subsequent faults. Protocol can therefore restore inter-agent continuity without eliminating the intra-agent restart discontinuity itself.",
        "",
        "## A11 — protocol plus persistence",
        "",
        "A11 has both immediate restart continuity (restart JS 0) and final correction retention 1.00. In this experiment it is the only arm that needs neither reconstruction after restart nor recovery from semantic overwrite.",
        "",
        "## Fault audit",
        "",
        "Each protocol arm receives the same four fault classes for all three agents. The fail-closed rejection totals are:",
        "",
    ]
    reasons = arms["A10"]["summary"]["protocol_rejection_reasons"]
    for reason, count in sorted(reasons.items()):
        lines.append(f"- `{reason}`: **{count}** rejections")
    lines += [
        "",
        "The conflict count is six because each of three agents receives two competing corrections with the same next version and parent; the protocol quarantines the whole fork rather than accepting the first arrival.",
        "",
        "## False-consensus result",
        "",
        f"The accepted median SCI has target JS **{ref['accepted_target_js']:.4f}**. The final no-protocol state has target JS **{arms['A00']['summary']['mean_final_target_js']:.4f}**, or **{false_consensus_ratio:.2f}×** the reference distortion, while final cross-agent JS is exactly **0.0000** because every agent converges to the same contaminated last write.",
        "",
        "Thus the temporal version of the EXP-0004 warning is explicit:",
        "",
        "$$",
        "\\text{persistent agreement} \\not\\Rightarrow \\text{persistent truth}",
        "$$",
        "",
        "Protocol protects the lineage of a correction; persistence protects the continuity of a cognition state. Neither metric should be replaced by consensus alone.",
        "",
        "## Hypothesis decisions",
        "",
    ]
    for key, value in h.items():
        lines.append(f"- {key}: **{value}**")
    lines += [
        "",
        "## Refined continuity model",
        "",
        "The bounded result motivates treating multi-agent cognition as two coupled continuity laws:",
        "",
        "$$",
        "\\text{Protocol} \\approx \\text{inter-agent continuity},",
        "$$",
        "",
        "$$",
        "\\text{Persistence} \\approx \\text{intra-agent continuity through time}.",
        "$$",
        "",
        "Their conjunction is a candidate mechanism for persistent shared cognition, but this experiment does not claim a universal theorem.",
        "",
        "## Non-claims",
        "",
        "- no new neural generalization claim; EXP-0005 operates on canonical EXP-0004 SCI packages;",
        "- no claim that the median package is universal truth; it is the experiment's accepted correction reference;",
        "- no claim that arbitrary production agents share F01–F19 coordinates;",
        "- no public AI Board write and no live CTCL verification;",
        "- no claim that protocol eliminates malicious authorized updates; this test covers explicit stale/provenance/rollback/fork faults;",
        "- no infinite-time cognition-continuity theorem.",
        "",
    ]
    return "\n".join(lines)


def run_and_write(repo_root: Path, out_dir: Path) -> dict:
    repo_root = Path(repo_root)
    out_dir = Path(out_dir)
    cfg = Exp0005Config()
    result = run_exp0005(repo_root, cfg)
    out_dir.mkdir(parents=True, exist_ok=True)

    write_json(out_dir / "config.json", {
        "config": result["config"],
        "factorial": ARM_FACTORS,
        "faults": ["stale_version", "missing_provenance", "rollback", "conflicting_correction"],
        "boundaries": result["boundaries"],
    })
    write_json(out_dir / "results/metrics.json", result)
    write_jsonl(out_dir / "results/per_arm_summary.jsonl", [
        {"arm": arm, **obj["factors"], **obj["summary"]} for arm, obj in sorted(result["arms"].items())
    ])
    write_jsonl(out_dir / "results/per_agent_summary.jsonl", [
        {
            "arm": arm,
            "agent": agent,
            **obj["factors"],
            "restart_js": row["restart_js"],
            "prebootstrap_retained": row["prebootstrap_retained"],
            "postbootstrap_retained": row["postbootstrap_retained"],
            "final_retained": row["final_retained"],
            "final_target_js": row["final_target_js"],
            "final_js_from_accepted": row["final_js_from_accepted"],
            "restart_history_count": row["restart_history_count"],
            "final_package_sha256": row["final_state"]["active_package"]["sha256"],
        }
        for arm, obj in sorted(result["arms"].items())
        for agent, row in sorted(obj["agents"].items())
    ])
    write_json(out_dir / "results/protocol_fault_audit.json", {
        arm: {
            agent: row["fault_records"]
            for agent, row in sorted(obj["agents"].items())
        }
        for arm, obj in sorted(result["arms"].items())
    })
    write_jsonl(out_dir / "ledger/ai_board_sci.jsonl", [
        {"arm": arm, **event}
        for arm, obj in sorted(result["arms"].items())
        for event in obj["ledger"]
    ])
    (out_dir / "results/report.md").parent.mkdir(parents=True, exist_ok=True)
    (out_dir / "results/report.md").write_text(render_report(result) + "\n", encoding="utf-8")

    export_three_m_v05(result, out_dir / "3m")
    verification = verify_three_m_v05(out_dir / "3m")
    write_json(out_dir / "3m/verification.json", verification)

    return {
        "experiment_id": "EXP-0005",
        "hypotheses": result["hypotheses"],
        "arm_summaries": {arm: obj["summary"] for arm, obj in sorted(result["arms"].items())},
        "three_m": verification,
    }


def main() -> None:
    summary = run_and_write(ROOT, ROOT / "experiments/EXP-0005")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
