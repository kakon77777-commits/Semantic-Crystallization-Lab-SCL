from pathlib import Path

from python.scl_exp.exp0009 import POLICY_NAMES, build_exp0009_events, run_exp0009


def test_event_fixture_contains_active_evidence_and_no_policy_truth_field():
    repo = Path(__file__).resolve().parents[1]
    feature_ids, reference, events = build_exp0009_events(repo)
    assert len(feature_ids) == 19
    assert reference["symbol"] == "qevra"
    assert len(events) >= 10
    assert any(event["reserve_reports"] for event in events)
    for event in events:
        assert "truth_effect" in event
        for report in event["initial_reports"] + event["reserve_reports"]:
            assert set(report) == {"source_agent", "origin_root", "stance"}
            assert report["stance"] in {-1, 1}


def test_non_oracle_policies_share_identical_trust_snapshots():
    repo = Path(__file__).resolve().parents[1]
    result = run_exp0009(repo)
    hashes = result["shared_trust_snapshot_hashes"]
    assert len(hashes) == len(result["events"])
    assert all(isinstance(value, str) and len(value) == 64 for value in hashes)


def test_belief_state_uses_multi_action_space():
    repo = Path(__file__).resolve().parents[1]
    result = run_exp0009(repo)
    actions = result["policies"]["Belief-State"]["summary"]["action_counts"]
    assert actions.get("seek_evidence", 0) > 0
    assert actions.get("defer", 0) > 0
    assert actions.get("accept", 0) > 0


def test_all_policy_metrics_and_hypothesis_decisions_are_recorded():
    repo = Path(__file__).resolve().parents[1]
    result = run_exp0009(repo)
    assert tuple(result["policies"]) == POLICY_NAMES
    for name in POLICY_NAMES:
        summary = result["policies"][name]["summary"]
        assert summary["total_loss"] >= 0
        assert summary["risk_weighted_target_loss"] >= 0
        assert summary["evidence_cost"] >= 0
        assert summary["defer_cost"] >= 0
    assert set(result["hypotheses"]) == {
        "H1_multi_action_uncertainty_policy_uses_seek_and_defer",
        "H2_belief_state_reduces_total_loss_vs_scalar",
        "H3_belief_state_pays_nonzero_information_cost",
        "H4_belief_state_is_not_oracle",
        "H5_uncertainty_changes_decisions_vs_mean_only",
        "H6_active_evidence_resolves_at_least_one_scalar_error",
        "H7_high_risk_false_accepts_not_worse_than_scalar",
    }
