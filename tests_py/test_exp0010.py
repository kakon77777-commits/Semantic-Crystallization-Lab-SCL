from pathlib import Path

from python.scl_exp.exp0010 import POLICY_NAMES, build_exp0010_events, run_exp0010


def test_exp0010_fixture_is_novel_and_split_into_transfer_and_meta_adversarial_phases():
    repo = Path(__file__).resolve().parents[1]
    feature_ids, reference, events, guard = build_exp0010_events(repo)
    assert len(feature_ids) == 19
    assert reference["symbol"] == "qevra"
    assert len(events) >= 12
    assert {event["phase"] for event in events} == {"novel_transfer", "meta_adversarial"}
    assert guard["candidate_hash_overlap_count"] == 0
    assert guard["all_event_ids_new"]
    assert len({event["candidate"]["sha256"] for event in events}) == len(events)


def test_artifact_exposure_and_order_are_explicitly_separated_between_policies():
    repo = Path(__file__).resolve().parents[1]
    result = run_exp0010(repo)
    assert tuple(result["policies"]) == POLICY_NAMES
    assert result["policies"]["A0-Reactive"]["reflexive_order"] == 0
    assert result["policies"]["A1-Artifact-Reflexive"]["reflexive_order"] == 1
    assert result["policies"]["A2-Second-Order"]["reflexive_order"] == 2
    assert result["artifact_pack"]["report_count"] == 9
    assert len(result["artifact_pack"]["report_sha256"]) == 9


def test_result_records_phase_losses_challenges_and_pre_registered_hypotheses_without_forcing_success():
    repo = Path(__file__).resolve().parents[1]
    result = run_exp0010(repo)
    for name in POLICY_NAMES:
        summary = result["policies"][name]["summary"]
        assert summary["total_loss"] >= 0
        assert set(summary["phase_loss"]) == {"novel_transfer", "meta_adversarial"}
    assert result["policies"]["A1-Artifact-Reflexive"]["summary"]["prospective_challenges"] > 0
    assert result["policies"]["A2-Second-Order"]["summary"]["second_order_challenges"] > 0
    assert set(result["hypotheses"]) == {
        "H1_artifact_pack_compiles_prior_failure_chain",
        "H2_a1_reduces_novel_transfer_loss_vs_a0",
        "H3_a1_catches_at_least_one_a0_high_confidence_error",
        "H4_meta_adversary_exploits_a1_rule",
        "H5_a2_reduces_meta_phase_loss_vs_a1",
        "H6_no_exact_candidate_reuse_from_prior_experiments",
        "H7_a2_is_not_oracle",
    }
