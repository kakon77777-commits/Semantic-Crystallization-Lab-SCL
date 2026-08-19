from pathlib import Path

from python.scl_exp.reflexive_artifact import compile_reflexive_rule_pack


def test_rule_pack_is_compiled_from_prior_artifacts_not_hardcoded_fixture_answers():
    repo = Path(__file__).resolve().parents[1]
    pack = compile_reflexive_rule_pack(repo)
    assert pack.report_count == 9
    assert len(pack.report_sha256) == 9
    assert all(len(value) == 64 for value in pack.report_sha256.values())
    assert pack.false_consensus_warning
    assert pack.structural_not_semantic_warning
    assert pack.static_quorum_tradeoff
    assert pack.reputation_hysteresis_warning
    assert pack.trust_state_decision_separation
    assert pack.reactive_uncertainty_too_late
    assert 0.0 < pack.prospective_challenge_threshold < 2.0


def test_rule_pack_records_explicit_validation_sources_for_meta_rules():
    repo = Path(__file__).resolve().parents[1]
    pack = compile_reflexive_rule_pack(repo)
    assert set(pack.validation_sha256) == {
        "EXP-0004", "EXP-0005", "EXP-0006", "EXP-0007", "EXP-0008", "EXP-0009"
    }
    assert all(len(value) == 64 for value in pack.validation_sha256.values())
