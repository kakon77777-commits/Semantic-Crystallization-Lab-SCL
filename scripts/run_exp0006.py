from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python.scl_exp.exp0006 import run_exp0006
from python.scl_exp.three_m_v06 import export_three_m_v06, verify_three_m_v06


BASE = ROOT / "experiments/EXP-0006"


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
    lines = [
        "# SCL EXP-0006 — Admissible Cognitive Transition Law / Plasticity–Integrity Tradeoff",
        "", "## Boundary", "",
        "EXP-0006 operates above the neural layer on the canonical EXP-0004 portable F01–F19 SCI package. It introduces a synthetic, explicit changing semantic ground truth solely to test transition-law behavior; it does not claim that this fixture is an ontology of real-world truth.",
        "",
        "All candidate transitions are structurally valid next-generation SCI updates with package hashes and provenance. The experiment therefore isolates the extra question: **should a structurally valid semantic transition be admitted?**",
        "", "## Policy comparison", "",
        "| Policy | Plasticity | Integrity | False reject | Pollution accept | Mean target JS | Final target JS | Mean genuine evidence |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ("Rigid", "Permissive", "Adaptive-Q2", "Adaptive-Q3"):
        s = arms[name]["summary"]
        ev = "—" if s["mean_accepted_genuine_evidence"] is None else f"{s['mean_accepted_genuine_evidence']:.2f}"
        lines.append(f"| {name} | {s['plasticity']:.3f} | {s['integrity']:.3f} | {s['false_reject_rate']:.3f} | {s['pollution_acceptance_rate']:.3f} | {s['mean_target_js']:.5f} | {s['final_target_js']:.5f} | {ev} |")

    q2 = arms["Adaptive-Q2"]["summary"]
    q3 = arms["Adaptive-Q3"]["summary"]
    lines += [
        "", "## Core result", "",
        "The experiment does **not** produce a universally dominant static transition threshold.", "",
        f"- Rigid: integrity={arms['Rigid']['summary']['integrity']:.1f}, plasticity={arms['Rigid']['summary']['plasticity']:.1f}; it never accepts pollution, but it also never learns the three genuine target shifts.",
        f"- Permissive: plasticity={arms['Permissive']['summary']['plasticity']:.1f}, integrity={arms['Permissive']['summary']['integrity']:.1f}; it tracks every genuine shift immediately but also accepts both structurally valid pollution events.",
        f"- Adaptive-Q2: plasticity={q2['plasticity']:.1f}, integrity={q2['integrity']:.1f}; it accepts the two-origin minority novelty and rejects the one-origin echo, but a two-origin coordinated attack crosses the same quorum.",
        f"- Adaptive-Q3: plasticity={q3['plasticity']:.3f}, integrity={q3['integrity']:.1f}; it blocks both attacks but false-rejects the genuine two-origin novelty until a later three-origin recovery arrives.",
        "", "Thus the bounded result is a literal plasticity–integrity frontier:", "", "$$",
        r"Q_2:\;\text{more plastic, less attack-resistant},", r"\qquad", r"Q_3:\;\text{less plastic, more attack-resistant}.", "$$", "",
        "Under this particular fixture, Adaptive-Q3 also has the lowest cumulative target distortion, but that does not remove its false rejection of genuine minority novelty. Which policy is preferable therefore depends on the loss assigned to delayed novelty versus admitted contamination.",
        "", "## Event-level audit", "",
    ]
    for name in ("Rigid", "Permissive", "Adaptive-Q2", "Adaptive-Q3"):
        lines.append(f"### {name}")
        for e in arms[name]["events"]:
            lines.append(f"- {e['event_id']} ({e['truth_effect']}): {'ACCEPT' if e['accepted'] else 'REJECT'}; reason={e['reason']}; origins={e['independent_origins']}; evidence={e['evidence_consumed']}; target JS={e['target_js']:.5f}.")
        lines.append("")

    lines += ["## Hypothesis decisions", ""]
    for key, value in result["hypotheses"].items():
        lines.append(f"- {key}: **{value}**")
    lines += [
        "", "## Interpretation", "",
        "EXP-0005 showed that structural protocol protects lineage and persistence protects temporal state. EXP-0006 adds a third requirement: an **admissibility law** must decide when a new, structurally valid cognition transition deserves to modify the imprint.", "",
        "A protocol that only proves `who/parent/version/hash` can still faithfully admit a bad semantic update. Conversely, a rule that never permits semantic change preserves integrity by making learning impossible. The hard problem is therefore not merely persistence or protocol conformance, but controlled revisability.",
        "", "## Non-claims", "",
        "- no claim that Q2 or Q3 is an optimal production threshold;",
        "- no claim that source-count equals epistemic independence in real systems; origin roots are an explicit bounded proxy;",
        "- no claim that the synthetic target shifts represent universal semantic truth;",
        "- no neural retraining, no public AI Board write, and no live CTCL call;",
        "- no theorem that every cognition system has the same plasticity–integrity frontier.", "",
    ]
    return "\n".join(lines)


def main() -> None:
    result = run_exp0006(ROOT)
    BASE.mkdir(parents=True, exist_ok=True)
    dump_json(BASE / "config.json", result["config"])
    dump_json(BASE / "results/metrics.json", result)

    event_rows = []
    ledger_rows = []
    for arm, arm_obj in sorted(result["arms"].items()):
        for index, row in enumerate(arm_obj["events"], start=1):
            compact = {"policy": arm, "sequence": index, **row}
            event_rows.append(compact)
            ledger_rows.append({
                "logical_instant": f"EXP0006-{arm}-{index:02d}",
                "event_type": "imprint.transition.accept" if row["accepted"] else "imprint.transition.objection",
                **compact,
            })
    dump_jsonl(BASE / "results/per_event_summary.jsonl", event_rows)
    dump_jsonl(BASE / "ledger/transition_events.jsonl", ledger_rows)
    (BASE / "results/report.md").write_text(make_report(result), encoding="utf-8", newline="\n")

    export_three_m_v06(result, BASE / "3m")
    verification = verify_three_m_v06(BASE / "3m")
    dump_json(BASE / "3m/verification.json", verification)
    print(json.dumps({
        "experiment": "EXP-0006",
        "hypotheses": result["hypotheses"],
        "three_m": verification,
        "summaries": {name: row["summary"] for name, row in result["arms"].items()},
    }, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
