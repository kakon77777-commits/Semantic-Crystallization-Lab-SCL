from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python.scl_exp.exp0009 import run_exp0009
from python.scl_exp.three_m_v09 import export_three_m_v09, verify_three_m_v09

BASE = ROOT / "experiments/EXP-0009"


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
    scalar = policies["Scalar-Threshold"]["summary"]
    mean = policies["Posterior-Mean"]["summary"]
    belief = policies["Belief-State"]["summary"]
    lines = [
        "# SCL EXP-0009 — Uncertainty-Aware Epistemic Decision", "", "## Boundary", "",
        "EXP-0009 holds the trust-memory trajectory fixed across all non-Oracle policies and changes only how that shared belief state is projected into action. Scalar-Threshold is binary accept/reject. Posterior-Mean may Accept/Reject/Seek Evidence/Defer using posterior mean only. Belief-State uses posterior mean plus trust uncertainty, volatility and disagreement. Oracle is an evaluation ceiling only.", "",
        "The current event truth label is never passed to a non-Oracle decision. Seek Evidence consumes a fixed cost and reveals one previously hidden report. Defer leaves the current SCI unchanged for one event and is resolved by the same one-event-delayed validation contract used by the audit layer.", "", "## Policy comparison", "",
        "| Policy | Total loss | Risk-target loss | Evidence cost | Defer cost | False accepts | False rejects | High-risk false accepts | Queries | Defers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ("Scalar-Threshold", "Posterior-Mean", "Belief-State", "Oracle"):
        s = policies[name]["summary"]
        lines.append(f"| {name} | {s['total_loss']:.5f} | {s['risk_weighted_target_loss']:.5f} | {s['evidence_cost']:.5f} | {s['defer_cost']:.5f} | {s['false_accepts']} | {s['false_rejects']} | {s['high_risk_false_accepts']} | {s['evidence_queries']} | {s['defer_count']} |")
    lines += ["", "## Core result — richer uncertainty helps one safety axis but loses overall", "",
        f"Belief-State reduces high-risk false accepts from **{scalar['high_risk_false_accepts']}** under Scalar-Threshold to **{belief['high_risk_false_accepts']}**, and it genuinely uses active evidence ({belief['evidence_queries']} queries) plus deferral ({belief['defer_count']} events). However its total loss is **{belief['total_loss']:.5f}**, worse than Scalar-Threshold at **{scalar['total_loss']:.5f}** and Posterior-Mean at **{mean['total_loss']:.5f}**. H2 is therefore **NOT SUPPORTED**.", "",
        "The main failure is temporal. Belief-State still accepts the first high-reputation A/B/C betrayal (E02) before volatility feedback is available. It then spends additional evidence/defer cost on later uncertainty while carrying distortion from that already-admitted bad transition. More expressive belief-state reasoning therefore does not automatically repair an earlier irreversible accept.", "",
        f"The preregistered active-evidence rescue gate also fails: there are **{result['active_evidence_scalar_errors_resolved']}** events where Scalar makes an immediate accept/reject error and Belief-State both seeks evidence and then resolves that same event into an immediate correct accept/reject. H6 is therefore **NOT SUPPORTED**.", "", "## Belief-State event audit", ""]
    for row in policies["Belief-State"]["events"]:
        trace = " → ".join(row["action_trace"])
        lines.append(f"- {row['event_id']} [{row['phase']}/{row['truth_effect']}]: {trace}; p={row['candidate_probability']:.3f}; uncertainty={row['uncertainty']:.3f}; disagreement={row['disagreement']:.3f}; queries={row['evidence_queries']}; target JS={row['target_js']:.5f}; total loss={row['total_loss']:.5f}.")
    lines += ["", "## Hypothesis decisions", ""]
    for key, value in result["hypotheses"].items(): lines.append(f"- {key}: **{value}**")
    lines += ["", "## Interpretation", "",
        "EXP-0008 separated trust-state quality from decision-policy quality. EXP-0009 confirms that simply exposing uncertainty/volatility to a multi-action policy is still insufficient. The decision layer can trade fewer high-risk false accepts for evidence cost, defer cost and delayed correction, yet remain vulnerable to the first trusted-coalition betrayal because the information needed to distrust it does not exist until after feedback.", "",
        "This points to a stronger next requirement: **active evidence selection must be prospective, not merely reactive to already-high uncertainty**. A system may need to model the value of challenging even a high-confidence coalition when semantic novelty/risk is extreme, rather than seeking only after its current belief state becomes visibly uncertain.", "", "## Non-claims", "",
        "- no claim that the hand-written uncertainty equation is production-optimal;", "- no claim that Scalar-Threshold is universally better; its lower loss is fixture- and cost-dependent;", "- no claim that Defer or Seek Evidence always has these costs in production;", "- no claim that one-event-delayed validation is always available;", "- no neural retraining, public AI Board write or live CTCL call;", "- no theorem that multi-action uncertainty policies must beat binary thresholds.", ""]
    return "\n".join(lines)


def main() -> None:
    result = run_exp0009(ROOT)
    BASE.mkdir(parents=True, exist_ok=True)
    dump_json(BASE / "config.json", result["config"])
    dump_json(BASE / "results/metrics.json", result)
    rows=[]; ledger=[]
    for policy, arm in sorted(result["policies"].items()):
        for sequence, row in enumerate(arm["events"], start=1):
            compact={"policy":policy,"sequence":sequence,**row}; rows.append(compact); ledger.append({"logical_instant":f"EXP0009-{policy}-{sequence:02d}","event_type":f"imprint.epistemic-decision.{row['final_action']}",**compact})
    dump_jsonl(BASE / "results/per_event_summary.jsonl", rows)
    dump_jsonl(BASE / "ledger/epistemic_decisions.jsonl", ledger)
    (BASE / "results/report.md").write_text(make_report(result), encoding="utf-8", newline="\n")
    export_three_m_v09(result, BASE / "3m")
    verification=verify_three_m_v09(BASE / "3m"); dump_json(BASE / "3m/verification.json", verification)
    print(json.dumps({"experiment":"EXP-0009","hypotheses":result["hypotheses"],"three_m":verification,"summaries":{name:arm["summary"] for name,arm in result["policies"].items()},"active_evidence_scalar_errors_resolved":result["active_evidence_scalar_errors_resolved"]}, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__": main()
