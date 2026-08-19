from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from .epistemic_decision import (
    BeliefStateDecisionPolicy,
    DecisionConfig,
    EvidenceReport,
    PosteriorMeanActivePolicy,
    ScalarThresholdPolicy,
)
from .grid import js_divergence
from .sci import build_sci_package, dense_signature
from .trust_dynamics import TrustDynamicsConfig, TrustDynamicsLedger


@dataclass(frozen=True)
class Exp0009Config:
    feature_space: str = "SCL-F01-F19-v0.2"
    risk_loss_weight: float = 3.0
    decision: DecisionConfig = DecisionConfig(
        base_accept_probability=0.64,
        risk_accept_weight=0.12,
        novelty_accept_weight=2.0,
        uncertainty_band_weight=0.14,
        max_seek=2,
        evidence_cost=0.0008,
        defer_cost=0.0012,
        seek_value_scale=0.22,
        seek_disagreement_weight=0.16,
        min_seek_signal=0.045,
    )
    trust: TrustDynamicsConfig = TrustDynamicsConfig(
        fixed_decay=0.90,
        adaptive_base_decay=0.97,
        volatility_decay_strength=0.42,
        min_decay=0.52,
        max_decay=0.995,
        surprise_ema=0.58,
        betrayal_boost=2.8,
        recovery_boost=2.2,
    )


POLICY_NAMES = ("Scalar-Threshold", "Posterior-Mean", "Belief-State", "Oracle")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_reference(repo_root: Path) -> tuple[list[str], dict]:
    metrics = _load_json(repo_root / "experiments/EXP-0004/results/metrics.json")
    return list(metrics["feature_ids"]), copy.deepcopy(metrics["packages"]["merged_qevra"])


def _clip(value: float) -> float:
    return float(min(1.0, max(0.0, value)))


def _reweight(package: dict, feature_ids: list[str], adjustments: dict[str, float], *, label: str) -> dict:
    values = dense_signature(package, feature_ids)
    idx = {fid: i for i, fid in enumerate(feature_ids)}
    for fid, delta in adjustments.items():
        values[idx[fid]] = _clip(float(values[idx[fid]]) + float(delta))
    return build_sci_package(
        package["symbol"], values, feature_ids, "exp0009-fixture", top_k=len(feature_ids),
        expansion=package.get("expansion", []),
        provenance={"exp0009_fixture": label, "from": package.get("sha256")},
    )


def _report(agent: str, root: str, stance: int) -> dict:
    return {"source_agent": str(agent), "origin_root": str(root), "stance": int(stance)}


def _reports(*items: tuple[str, str, int]) -> list[dict]:
    return [_report(*item) for item in items]


def _target_js(package: dict, target: dict, feature_ids: list[str]) -> float:
    return js_divergence(dense_signature(package, feature_ids), dense_signature(target, feature_ids))


def _candidate_novelty(active: dict, candidate: dict, feature_ids: list[str]) -> float:
    return js_divergence(dense_signature(active, feature_ids), dense_signature(candidate, feature_ids))


def _all_reports(event: dict) -> list[dict]:
    return list(event["initial_reports"]) + list(event["reserve_reports"])


def _feedback_roots(event: dict) -> tuple[list[str], list[str]]:
    correct: set[str] = set()
    incorrect: set[str] = set()
    genuine = event["truth_effect"] == "genuine"
    for row in _all_reports(event):
        supports = int(row["stance"]) > 0
        is_correct = supports if genuine else not supports
        (correct if is_correct else incorrect).add(str(row["origin_root"]))
    overlap = correct & incorrect
    if overlap:
        raise ValueError(f"conflicting audit labels for roots: {sorted(overlap)}")
    return sorted(correct), sorted(incorrect)


def _calibration_events(reference: dict, feature_ids: list[str]) -> list[dict]:
    truth = copy.deepcopy(reference)
    events: list[dict] = []
    def add(event_id: str, truth_effect: str, reports: list[dict], adjustments: dict[str, float]) -> None:
        nonlocal truth
        candidate = _reweight(truth, feature_ids, adjustments, label=event_id)
        if truth_effect == "genuine": truth = copy.deepcopy(candidate)
        events.append({"event_id": event_id, "truth_effect": truth_effect, "initial_reports": reports, "reserve_reports": [], "candidate": candidate})
    add("C01_ABC_good", "genuine", _reports(("c1a", "A", 1), ("c1b", "B", 1), ("c1c", "C", 1)), {"F18": +0.04})
    add("C02_AB_good", "genuine", _reports(("c2a", "A", 1), ("c2b", "B", 1)), {"F05": +0.04})
    add("C03_X_bad", "pollution", _reports(("c3x", "X", 1), ("c3a", "A", -1)), {"F19": +0.20})
    add("C04_ABC_good", "genuine", _reports(("c4a", "A", 1), ("c4b", "B", 1), ("c4c", "C", 1)), {"F17": +0.04})
    add("C05_DE_emerge", "genuine", _reports(("c5d", "D", 1), ("c5e", "E", 1), ("c5b", "B", 1)), {"F12": +0.04})
    add("C06_ADF_bridge", "genuine", _reports(("c6a", "A", 1), ("c6d", "D", 1), ("c6f", "F", 1)), {"F15": +0.03})
    return events


def build_exp0009_events(repo_root: Path) -> tuple[list[str], dict, list[dict]]:
    feature_ids, reference = _load_reference(Path(repo_root)); truth = copy.deepcopy(reference); events: list[dict] = []
    def genuine(event_id, phase, risk, initial, reserve, adjustments):
        nonlocal truth
        before = copy.deepcopy(truth); candidate = _reweight(truth, feature_ids, adjustments, label=event_id); truth = copy.deepcopy(candidate)
        events.append({"event_id":event_id,"phase":phase,"truth_effect":"genuine","risk":float(risk),"initial_reports":initial,"reserve_reports":reserve,"candidate":candidate,"truth_before":before,"truth_after":copy.deepcopy(truth)})
    def pollution(event_id, phase, risk, initial, reserve, adjustments):
        candidate = _reweight(truth, feature_ids, adjustments, label=event_id)
        events.append({"event_id":event_id,"phase":phase,"truth_effect":"pollution","risk":float(risk),"initial_reports":initial,"reserve_reports":reserve,"candidate":candidate,"truth_before":copy.deepcopy(truth),"truth_after":copy.deepcopy(truth)})
    genuine("E01_minority_disagreement","minority_novelty",0.55,_reports(("e1d","D",1),("e1e","E",-1)),_reports(("e1a","A",1),("e1f","F",1)),{"F04":+0.055,"F14":+0.025})
    pollution("E02_trusted_betrayal_1","trusted_betrayal",0.90,_reports(("e2a","A",1),("e2b","B",1),("e2c","C",1)),_reports(("e2d","D",-1),("e2e","E",-1)),{"F19":+0.42,"F16":-0.10})
    pollution("E03_trusted_betrayal_2","trusted_betrayal",0.80,_reports(("e3a","A",1),("e3b","B",1)),_reports(("e3d","D",-1),("e3f","F",-1)),{"F19":+0.36,"F10":-0.10})
    genuine("E04_recovery_DE","recovery",0.45,_reports(("e4d","D",1),("e4e","E",1)),_reports(("e4c","C",1)),{"F11":+0.05,"F03":+0.03})
    genuine("E05_structured_split_genuine","structured_disagreement",0.65,_reports(("e5a","A",1),("e5c","C",-1)),_reports(("e5d","D",1),("e5f","F",1)),{"F08":+0.05,"F18":+0.03})
    pollution("E06_correlated_echo","structured_disagreement",0.40,_reports(("e6x1","X",1),("e6x2","X",1),("e6x3","X",1)),_reports(("e6a","A",-1)),{"F19":+0.28,"F07":-0.08})
    genuine("E07_high_risk_genuine","high_risk",0.85,_reports(("e7d","D",1),("e7f","F",1)),_reports(("e7e","E",1),("e7b","B",-1)),{"F06":+0.05,"F16":+0.04})
    pollution("E08_high_risk_pollution","high_risk",0.90,_reports(("e8b","B",1),("e8c","C",1)),_reports(("e8d","D",-1),("e8e","E",-1),("e8f","F",-1)),{"F19":+0.40,"F01":-0.09})
    genuine("E09_new_sources_split","new_sources",0.50,_reports(("e9g","G",1),("e9h","H",-1)),_reports(("e9d","D",1),("e9f","F",1)),{"F09":+0.06,"F14":+0.035})
    pollution("E10_opposed_pollution","new_sources",0.75,_reports(("e10a","A",1),("e10d","D",-1)),_reports(("e10e","E",-1),("e10f","F",-1)),{"F19":+0.33,"F12":-0.09})
    genuine("E11_low_risk_unresolved","defer_case",0.25,_reports(("e11g","G",1),("e11h","H",-1)),[],{"F02":+0.045,"F15":+0.03})
    genuine("E12_final_convergence","recovery",0.60,_reports(("e12a","A",1),("e12d","D",1),("e12f","F",1)),_reports(("e12e","E",1)),{"F10":+0.045,"F17":+0.035})
    return feature_ids, reference, events


def _snapshot_hash(snapshot: dict) -> str:
    return hashlib.sha256(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _apply_feedback(ledger: TrustDynamicsLedger, event: dict) -> None:
    good,bad=_feedback_roots(event)
    if good: ledger.observe(good,genuine=True)
    if bad: ledger.observe(bad,genuine=False)


def _shared_trust_snapshots(reference, feature_ids, events, cfg):
    ledger=TrustDynamicsLedger("adaptive",cfg.trust); previous=None
    for event in _calibration_events(reference,feature_ids):
        ledger.advance()
        if previous is not None: _apply_feedback(ledger,previous)
        previous=event
    ledger.advance()
    if previous is not None: _apply_feedback(ledger,previous)
    snapshots=[]; previous_eval=None
    for event in events:
        if previous_eval is not None:
            ledger.advance(); _apply_feedback(ledger,previous_eval)
        snapshots.append(ledger.snapshot()); previous_eval=event
    return snapshots


def _policy(name,cfg):
    if name=="Scalar-Threshold": return ScalarThresholdPolicy(cfg.decision)
    if name=="Posterior-Mean": return PosteriorMeanActivePolicy(cfg.decision)
    if name=="Belief-State": return BeliefStateDecisionPolicy(cfg.decision)
    return None


def _simulate_policy(name, reference, feature_ids, events, snapshots, cfg):
    state=copy.deepcopy(reference); pending=None; rows=[]; action_counts=Counter(); policy=_policy(name,cfg)
    for event,trust_snapshot in zip(events,snapshots):
        pending_resolution=None
        if pending is not None:
            if pending["truth_effect"]=="genuine": state=copy.deepcopy(pending["candidate"]); pending_resolution="accepted_after_delayed_validation"
            else: pending_resolution="discarded_after_delayed_validation"
            pending=None
        evidence=[EvidenceReport(**row) for row in event["initial_reports"]]; reserve=[EvidenceReport(**row) for row in event["reserve_reports"]]; novelty=_candidate_novelty(state,event["candidate"],feature_ids); trace=[]; seek_count=0; last_decision=None
        if name=="Oracle":
            final_action="accept" if event["truth_effect"]=="genuine" else "reject"; trace=[final_action]; action_counts[final_action]+=1; candidate_probability=1.0 if final_action=="accept" else 0.0; uncertainty=0.0; disagreement=0.0; reason="oracle_truth_ceiling"
        else:
            while True:
                last_decision=policy.decide(evidence,trust_snapshot,risk=event["risk"],novelty_js=novelty,evidence_available=seek_count<len(reserve),seek_count=seek_count)
                trace.append(last_decision.action); action_counts[last_decision.action]+=1
                if last_decision.action!="seek_evidence": break
                evidence.append(reserve[seek_count]); seek_count+=1
            final_action=last_decision.action; candidate_probability=float(last_decision.candidate_probability); uncertainty=float(last_decision.uncertainty); disagreement=float(last_decision.disagreement); reason=last_decision.reason
        if final_action=="accept": state=copy.deepcopy(event["candidate"])
        elif final_action=="defer": pending={"candidate":copy.deepcopy(event["candidate"]),"truth_effect":event["truth_effect"],"event_id":event["event_id"]}
        target_js=_target_js(state,event["truth_after"],feature_ids); target_loss=target_js*(1.0+cfg.risk_loss_weight*event["risk"]); evidence_cost=seek_count*cfg.decision.evidence_cost if name!="Oracle" else 0.0; defer_cost=cfg.decision.defer_cost*(1.0+event["risk"]) if final_action=="defer" and name!="Oracle" else 0.0; total_loss=target_loss+evidence_cost+defer_cost
        correct_immediate=(event["truth_effect"]=="genuine" and final_action=="accept") or (event["truth_effect"]=="pollution" and final_action=="reject")
        rows.append({"event_id":event["event_id"],"phase":event["phase"],"truth_effect":event["truth_effect"],"risk":event["risk"],"initial_evidence_count":len(event["initial_reports"]),"reserve_evidence_count":len(event["reserve_reports"]),"evidence_queries":seek_count,"action_trace":trace,"final_action":final_action,"reason":reason,"candidate_probability":candidate_probability,"uncertainty":uncertainty,"disagreement":disagreement,"novelty_js":float(novelty),"target_js":float(target_js),"risk_weighted_target_loss":float(target_loss),"evidence_cost":float(evidence_cost),"defer_cost":float(defer_cost),"total_loss":float(total_loss),"correct_immediate":bool(correct_immediate),"pending_resolution_before_event":pending_resolution,"trust_snapshot_sha256":_snapshot_hash(trust_snapshot)})
    genuine=[r for r in rows if r["truth_effect"]=="genuine"]; pollution=[r for r in rows if r["truth_effect"]=="pollution"]
    summary={"events":len(rows),"total_loss":float(sum(r["total_loss"] for r in rows)),"risk_weighted_target_loss":float(sum(r["risk_weighted_target_loss"] for r in rows)),"evidence_cost":float(sum(r["evidence_cost"] for r in rows)),"defer_cost":float(sum(r["defer_cost"] for r in rows)),"mean_target_js":float(sum(r["target_js"] for r in rows)/len(rows)),"false_accepts":int(sum(r["final_action"]=="accept" for r in pollution)),"false_rejects":int(sum(r["final_action"]=="reject" for r in genuine)),"defer_count":int(sum(r["final_action"]=="defer" for r in rows)),"evidence_queries":int(sum(r["evidence_queries"] for r in rows)),"high_risk_false_accepts":int(sum(r["final_action"]=="accept" and r["risk"]>=0.7 for r in pollution)),"action_counts":dict(sorted(action_counts.items())),"immediate_accuracy":float(sum(r["correct_immediate"] for r in rows)/len(rows))}
    return {"summary":summary,"events":rows}


def run_exp0009(repo_root: Path, config: Exp0009Config | None = None) -> dict:
    repo_root=Path(repo_root); cfg=config or Exp0009Config(); feature_ids,reference,events=build_exp0009_events(repo_root); snapshots=_shared_trust_snapshots(reference,feature_ids,events,cfg); policies={name:_simulate_policy(name,reference,feature_ids,events,snapshots,cfg) for name in POLICY_NAMES}
    scalar_rows={r["event_id"]:r for r in policies["Scalar-Threshold"]["events"]}; belief_rows={r["event_id"]:r for r in policies["Belief-State"]["events"]}; mean_rows={r["event_id"]:r for r in policies["Posterior-Mean"]["events"]}; resolved=0
    for event in events:
        sid=event["event_id"]; s=scalar_rows[sid]; b=belief_rows[sid]; scalar_wrong=(event["truth_effect"]=="genuine" and s["final_action"]=="reject") or (event["truth_effect"]=="pollution" and s["final_action"]=="accept"); belief_correct_after_seek=b["evidence_queries"]>0 and ((event["truth_effect"]=="genuine" and b["final_action"]=="accept") or (event["truth_effect"]=="pollution" and b["final_action"]=="reject")); resolved += int(scalar_wrong and belief_correct_after_seek)
    hypotheses={"H1_multi_action_uncertainty_policy_uses_seek_and_defer":policies["Belief-State"]["summary"]["evidence_queries"]>0 and policies["Belief-State"]["summary"]["defer_count"]>0,"H2_belief_state_reduces_total_loss_vs_scalar":policies["Belief-State"]["summary"]["total_loss"]<policies["Scalar-Threshold"]["summary"]["total_loss"],"H3_belief_state_pays_nonzero_information_cost":policies["Belief-State"]["summary"]["evidence_cost"]>0,"H4_belief_state_is_not_oracle":policies["Belief-State"]["summary"]["total_loss"]>policies["Oracle"]["summary"]["total_loss"],"H5_uncertainty_changes_decisions_vs_mean_only":any(belief_rows[eid]["action_trace"]!=mean_rows[eid]["action_trace"] for eid in belief_rows),"H6_active_evidence_resolves_at_least_one_scalar_error":resolved>0,"H7_high_risk_false_accepts_not_worse_than_scalar":policies["Belief-State"]["summary"]["high_risk_false_accepts"]<=policies["Scalar-Threshold"]["summary"]["high_risk_false_accepts"]}
    return {"schema":"scl-exp0009/v0.1","experiment_id":"EXP-0009","title":"Uncertainty-Aware Epistemic Decision","feature_ids":feature_ids,"config":asdict(cfg),"boundaries":{"current_truth_visible_to_non_oracle_policy":False,"shared_trust_memory_across_non_oracle_policies":True,"trust_feedback_mode":"one-event-delayed external audit","defer_resolution_mode":"one-event-delayed validation","seek_evidence_costed":True,"oracle_is_evaluation_ceiling_only":True,"neural_retraining":False,"public_ai_board_write":False,"live_ctcl_call":False},"events":[{k:v for k,v in event.items() if k not in {"candidate","truth_before","truth_after"}} for event in events],"shared_trust_snapshot_hashes":[_snapshot_hash(snapshot) for snapshot in snapshots],"policies":policies,"active_evidence_scalar_errors_resolved":int(resolved),"hypotheses":hypotheses}
