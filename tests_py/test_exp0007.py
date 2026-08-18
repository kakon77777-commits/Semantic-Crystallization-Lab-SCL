import unittest
from pathlib import Path

from python.scl_exp.exp0007 import run_exp0007


class Exp0007Tests(unittest.TestCase):
    def test_benchmark_has_delayed_feedback_and_oracle_ceiling(self):
        repo = Path(__file__).resolve().parents[1]
        result = run_exp0007(repo)
        self.assertEqual(result["experiment_id"], "EXP-0007")
        self.assertEqual(len(result["event_fixtures"]), 15)
        self.assertEqual(result["boundaries"]["feedback_mode"], "one_event_delayed")
        oracle = result["arms"]["Oracle"]["summary"]
        self.assertEqual(oracle["plasticity"], 1.0)
        self.assertEqual(oracle["integrity"], 1.0)
        self.assertEqual(oracle["false_accept_rate"], 0.0)
        self.assertEqual(oracle["false_reject_rate"], 0.0)

    def test_static_quorums_form_a_plasticity_integrity_tradeoff(self):
        repo = Path(__file__).resolve().parents[1]
        result = run_exp0007(repo)
        q2 = result["arms"]["Static-Q2"]["summary"]
        q3 = result["arms"]["Static-Q3"]["summary"]
        self.assertGreater(q2["plasticity"], q3["plasticity"])
        self.assertLess(q2["integrity"], q3["integrity"])

    def test_learned_policy_records_dynamic_threshold_and_trust_drift(self):
        repo = Path(__file__).resolve().parents[1]
        result = run_exp0007(repo)
        learned = result["arms"]["Learned-Adaptive"]
        self.assertTrue(all("required_support" in row for row in learned["events"]))
        self.assertTrue(all("trust_before" in row for row in learned["events"]))
        drift = learned["trust_drift"]
        self.assertGreater(drift["B_phase1"], drift["B_final"])
        self.assertGreater(drift["D_final"], drift["D_initial"])


if __name__ == "__main__":
    unittest.main()
