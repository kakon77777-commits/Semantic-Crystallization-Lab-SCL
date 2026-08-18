from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from .cross_agent import align_symbol_to_signature
from .exp0003 import Exp0003Config, _evaluate_symbol_contexts, prepare_stage2_state
from .experiment import ExperimentConfig
from .grid import js_divergence
from .sci import build_sci_package, contaminate_package, dense_signature, objection_records, robust_merge_packages
from .sci_ledger import SciLedger
from .stability import mean_pairwise_js, mean_support_jaccard
from .stability_corpus import FULL_Q, build_eval_contexts


@dataclass(frozen=True)
class Exp0004Config:
    stage2: ExperimentConfig = field(default_factory=lambda: ExperimentConfig(
        d_model=48,
        nhead=4,
        layers=1,
        max_len=384,
        base_epochs=90,
        stage1_epochs=120,
        stage2_epochs=120,
        learning_rate=0.012,
        support_threshold=0.5,
        rms_factor=1.0,
        positive_weight_cap=8.0,
    ))
    transfer_epochs: int = 80
    transfer_lr: float = 0.015
    qevra_top_k: int = 18
    tivak_top_k: int = 1
    objection_threshold: float = 0.12
    contamination_f19: float = 0.98
    contamination_f07: float = 0.05
    contamination_f14: float = 0.05


def _pairwise_support_jaccard(supports: list[set[str]]) -> float:
    return mean_support_jaccard(supports)


def phase_summary(evals: dict[str, dict], feature_ids: list[str], target: np.ndarray, *, threshold: float) -> dict:
    names = sorted(evals)
    q = np.stack([np.asarray(evals[n]["qevra"]["centroid"], dtype=float) for n in names])
    t = np.stack([np.asarray(evals[n]["tivak"]["centroid"], dtype=float) for n in names])
    q_supports = [set(evals[n]["qevra"].get("support") or [fid for fid, value in zip(feature_ids, q[i]) if value >= threshold]) for i, n in enumerate(names)]
    t_supports = [set(evals[n]["tivak"].get("support") or [fid for fid, value in zip(feature_ids, t[i]) if value >= threshold]) for i, n in enumerate(names)]
    target_set = {fid for fid, value in zip(feature_ids, target) if value > 0.5}
    q_recalls = [len(s & target_set) / len(target_set) for s in q_supports]
    return {
        "agents": names,
        "qevra_cross_agent_js": mean_pairwise_js(q),
        "qevra_support_jaccard": _pairwise_support_jaccard(q_supports),
        "qevra_mean_target_js": float(np.mean([js_divergence(row, target) for row in q])),
        "qevra_mean_target_recall": float(np.mean(q_recalls)),
        "qevra_mean_f19": float(np.mean(q[:, feature_ids.index("F19")])),
        "qevra_reverse_top1_rate": float(np.mean([float(evals[n]["qevra"].get("reverse_top1_rate", 0.0)) for n in names])),
        "tivak_cross_agent_js": mean_pairwise_js(t),
        "tivak_support_jaccard": _pairwise_support_jaccard(t_supports),
        "tivak_mean_f19": float(np.mean(t[:, feature_ids.index("F19")])),
        "tivak_mean_support_count": float(np.mean([len(s) for s in t_supports])),
        "qevra_mean_support_count": float(np.mean([len(s) for s in q_supports])),
    }


def _normalized_eval(raw: dict, feature_ids: list[str], threshold: float) -> dict:
    out = {}
    for symbol in ("qevra", "tivak"):
        row = raw[symbol]
        centroid = np.asarray(row["centroid"], dtype=float)
        out[symbol] = {
            "centroid": [float(x) for x in centroid],
            "support": [fid for fid, value in zip(feature_ids, centroid) if float(value) >= threshold],
            "reverse_top1_rate": float(row["reverse_top1_rate"]),
            "context_js": float(row["mean_pairwise_js"]),
            "intrinsic_support_jaccard": float(row["support_jaccard"]),
            "target_recall": float(row["target_recall_mean"]),
            "centroid_target_js": float(row["centroid_target_js"]),
        }
    return out


def _evaluate_model(state: dict, model, eval_cfg: Exp0003Config, contexts: dict[str, list[str]]) -> dict:
    raw, _ = _evaluate_symbol_contexts(model, state["tokenizer"], state["feature_ids"], contexts, eval_cfg)
    return _normalized_eval(raw, state["feature_ids"], eval_cfg.stage2.support_threshold)


def _clone_and_align(state: dict, q_package: dict, t_package: dict, cfg: Exp0004Config, eval_cfg: Exp0003Config, contexts: dict[str, list[str]]) -> tuple[dict, dict]:
    model = copy.deepcopy(state["model"])
    feature_ids = state["feature_ids"]
    q_update = align_symbol_to_signature(
        model, state["tokenizer"], "qevra", dense_signature(q_package, feature_ids),
        epochs=cfg.transfer_epochs, lr=cfg.transfer_lr, max_len=cfg.stage2.max_len,
    )
    t_update = align_symbol_to_signature(
        model, state["tokenizer"], "tivak", dense_signature(t_package, feature_ids),
        epochs=cfg.transfer_epochs, lr=cfg.transfer_lr, max_len=cfg.stage2.max_len,
    )
    return _evaluate_model(state, model, eval_cfg, contexts), {"qevra": q_update, "tivak": t_update}


def _receiver_donor_js(evals: dict[str, dict], donor: str = "agent-A") -> dict[str, float]:
    donor_sig = np.asarray(evals[donor]["qevra"]["centroid"], dtype=float)
    return {name: js_divergence(np.asarray(row["qevra"]["centroid"], dtype=float), donor_sig) for name, row in evals.items() if name != donor}


def run_exp0004(repo_root: Path, seeds: tuple[int, int, int] = (11, 23, 37), config: Exp0004Config | None = None) -> dict:
    repo_root = Path(repo_root)
    cfg = config or Exp0004Config()
    eval_cfg = Exp0003Config(stage2=cfg.stage2, arm_epochs=60, cycles=3, cycle_epochs=20)
    contexts = build_eval_contexts()
    agent_names = ["agent-A", "agent-B", "agent-C"]
    states = {name: prepare_stage2_state(repo_root, seed, cfg.stage2) for name, seed in zip(agent_names, seeds)}
    feature_ids = states["agent-A"]["feature_ids"]
    target = np.array([1.0 if fid in set(FULL_Q) else 0.0 for fid in feature_ids], dtype=float)

    initial = {name: _evaluate_model(state, state["model"], eval_cfg, contexts) for name, state in states.items()}
    initial_summary = phase_summary(initial, feature_ids, target, threshold=cfg.stage2.support_threshold)

    q_packages = {
        name: build_sci_package("qevra", row["qevra"]["centroid"], feature_ids, name, top_k=cfg.qevra_top_k,
                                provenance={"phase": "independent-reconstruction", "seed": seed})
        for (name, row), seed in zip(initial.items(), seeds)
    }
    t_packages = {
        name: build_sci_package("tivak", row["tivak"]["centroid"], feature_ids, name, top_k=cfg.tivak_top_k, expansion=[],
                                provenance={"phase": "pointer-control", "seed": seed})
        for (name, row), seed in zip(initial.items(), seeds)
    }

    donor_transfer = {"agent-A": initial["agent-A"]}
    donor_updates = {"agent-A": {"qevra": None, "tivak": None}}
    for name in ("agent-B", "agent-C"):
        donor_transfer[name], donor_updates[name] = _clone_and_align(states[name], q_packages["agent-A"], t_packages["agent-A"], cfg, eval_cfg, contexts)
    donor_summary = phase_summary(donor_transfer, feature_ids, target, threshold=cfg.stage2.support_threshold)

    objections = {
        name: objection_records(q_packages["agent-A"], q_packages[name], feature_ids, threshold=cfg.objection_threshold)
        for name in ("agent-B", "agent-C")
    }
    merged_q = robust_merge_packages(list(q_packages.values()), feature_ids, source_agent="board-median-merge")
    merged_t = robust_merge_packages(list(t_packages.values()), feature_ids, source_agent="board-pointer-median")
    merged_eval, merged_updates = {}, {}
    for name in agent_names:
        merged_eval[name], merged_updates[name] = _clone_and_align(states[name], merged_q, merged_t, cfg, eval_cfg, contexts)
    merged_summary = phase_summary(merged_eval, feature_ids, target, threshold=cfg.stage2.support_threshold)

    contaminated_q = contaminate_package(
        merged_q,
        feature_ids,
        boost={"F19": cfg.contamination_f19},
        suppress={"F07": cfg.contamination_f07, "F14": cfg.contamination_f14},
    )
    contaminated_eval, contaminated_updates = {}, {}
    for name in agent_names:
        contaminated_eval[name], contaminated_updates[name] = _clone_and_align(states[name], contaminated_q, merged_t, cfg, eval_cfg, contexts)
    contaminated_summary = phase_summary(contaminated_eval, feature_ids, target, threshold=cfg.stage2.support_threshold)

    initial_donor_js = _receiver_donor_js(initial)
    transfer_donor_js = _receiver_donor_js(donor_transfer)
    h2_per_receiver = {}
    for receiver in ("agent-B", "agent-C"):
        before_target = js_divergence(np.asarray(initial[receiver]["qevra"]["centroid"]), target)
        after_target = js_divergence(np.asarray(donor_transfer[receiver]["qevra"]["centroid"]), target)
        h2_per_receiver[receiver] = {
            "donor_js_before": initial_donor_js[receiver],
            "donor_js_after": transfer_donor_js[receiver],
            "target_js_before": before_target,
            "target_js_after": after_target,
            "pass": transfer_donor_js[receiver] < initial_donor_js[receiver] and after_target <= before_target,
        }

    donor_effect = {
        "mean_receiver_to_donor_js_before": float(np.mean([v["donor_js_before"] for v in h2_per_receiver.values()])),
        "mean_receiver_to_donor_js_after": float(np.mean([v["donor_js_after"] for v in h2_per_receiver.values()])),
        "mean_receiver_target_js_before": float(np.mean([v["target_js_before"] for v in h2_per_receiver.values()])),
        "mean_receiver_target_js_after": float(np.mean([v["target_js_after"] for v in h2_per_receiver.values()])),
    }
    donor_effect["consensus_gain_fraction"] = 1.0 - donor_effect["mean_receiver_to_donor_js_after"] / donor_effect["mean_receiver_to_donor_js_before"]
    donor_effect["target_distortion_multiplier"] = donor_effect["mean_receiver_target_js_after"] / donor_effect["mean_receiver_target_js_before"]

    hypotheses = {
        "H1_independent_divergence_exists": initial_summary["qevra_cross_agent_js"] > 0.0,
        "H2_donor_transfer_success": sum(1 for v in h2_per_receiver.values() if v["pass"]) >= 2,
        "H2_receiver_details": h2_per_receiver,
        "H3_median_correction_success": merged_summary["qevra_cross_agent_js"] < initial_summary["qevra_cross_agent_js"] and merged_summary["qevra_mean_target_js"] <= initial_summary["qevra_mean_target_js"],
        "H4_false_consensus_possible": contaminated_summary["qevra_cross_agent_js"] <= initial_summary["qevra_cross_agent_js"] and contaminated_summary["qevra_mean_target_js"] > initial_summary["qevra_mean_target_js"],
        "H5_pointer_control_narrow": merged_summary["tivak_mean_f19"] > merged_summary["qevra_mean_f19"] and merged_summary["tivak_mean_support_count"] < merged_summary["qevra_mean_support_count"],
        "E1_donor_induced_false_consensus_observed": donor_effect["mean_receiver_to_donor_js_after"] < donor_effect["mean_receiver_to_donor_js_before"] and donor_effect["mean_receiver_target_js_after"] > donor_effect["mean_receiver_target_js_before"],
    }

    ledger = SciLedger(topic="scl-exp0004-cross-agent-sci")
    for name in agent_names:
        ledger.append("imprint.proposal", name, {"qevra_package_sha256": q_packages[name]["sha256"], "tivak_package_sha256": t_packages[name]["sha256"]})
    for name in ("agent-B", "agent-C"):
        ledger.append("imprint.objection", name, {"against": q_packages["agent-A"]["sha256"], "objections": objections[name]})
        ledger.append("imprint.correction", name, {"replacement_package_sha256": q_packages[name]["sha256"], "objection_count": len(objections[name])})
    ledger.append("imprint.merge", "board-median-merge", {"package_sha256": merged_q["sha256"], "method": "coordinatewise-median"})
    for name in ("agent-B", "agent-C"):
        ledger.append("imprint.transfer", "agent-A", {"to": name, "package_sha256": q_packages["agent-A"]["sha256"], "mode": "donor-transfer"})
    for name in agent_names:
        ledger.append("imprint.transfer", "board-median-merge", {"to": name, "package_sha256": merged_q["sha256"], "mode": "corrected-merge"})
    ledger.append("imprint.contamination", "shared-correlated-source", {"package_sha256": contaminated_q["sha256"], "boost": {"F19": cfg.contamination_f19}, "suppress": {"F07": cfg.contamination_f07, "F14": cfg.contamination_f14}})

    source_bytes = len((repo_root / "experiments/EXP-0001/source/source.zh.txt").read_bytes())
    package_bytes = len(json.dumps(q_packages["agent-A"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))

    return {
        "schema": "scl-exp0004/v0.4",
        "experiment_id": "EXP-0004",
        "sci_definition": "Symbolic Cognitive Imprint (SCI) / 符號認知印刻",
        "seeds": list(seeds),
        "feature_ids": feature_ids,
        "config": asdict(cfg),
        "boundaries": {
            "cross_agent_coordinate": "shared F01-F19 feature space only",
            "hidden_coordinate_comparison": False,
            "public_ai_board_write": False,
            "live_ctcl_call": False,
        },
        "package_cost": {"donor_qevra_package_bytes": package_bytes, "source_prose_bytes": source_bytes, "ratio_source_to_package": source_bytes / package_bytes},
        "packages": {"qevra": q_packages, "tivak": t_packages, "merged_qevra": merged_q, "merged_tivak": merged_t, "contaminated_qevra": contaminated_q},
        "objections": objections,
        "phases": {
            "independent": {"agents": initial, "summary": initial_summary},
            "donor_transfer": {"agents": donor_transfer, "summary": donor_summary, "updates": donor_updates},
            "median_correction": {"agents": merged_eval, "summary": merged_summary, "updates": merged_updates},
            "correlated_contamination": {"agents": contaminated_eval, "summary": contaminated_summary, "updates": contaminated_updates},
        },
        "hypotheses": hypotheses,
        "donor_transfer_effect": donor_effect,
        "ledger": ledger.events,
    }
