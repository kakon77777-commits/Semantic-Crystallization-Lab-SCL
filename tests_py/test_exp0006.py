import unittest
from pathlib import Path

from python.scl_exp.exp0006 import run_exp0006


class Exp0006Tests(unittest.TestCase):
    def test_plasticity_integrity_frontier_is_explicit(self):
        root = Path(__file__).resolve().parents[1]
        result = run_exp0006(root)
        self.assertEqual(set(result["arms"]), {"Rigid", "Permissive", "Adaptive-Q2", "Adaptive-Q3"})

        rigid = result["arms"]["Rigid"]["summary"]
        permissive = result["arms"]["Permissive"]["summary"]
        q2 = result["arms"]["Adaptive-Q2"]["summary"]
        q3 = result["arms"]["Adaptive-Q3"]["summary"]

        self.assertEqual(rigid["plasticity"], 0.0)
        self.assertEqual(rigid["integrity"], 1.0)
        self.assertEqual(permissive["plasticity"], 1.0)
        self.assertEqual(permissive["integrity"], 0.0)
        self.assertEqual(q2["plasticity"], 1.0)
        self.assertEqual(q2["integrity"], 0.5)
        self.assertAlmostEqual(q3["plasticity"], 2.0 / 3.0)
        self.assertEqual(q3["integrity"], 1.0)
        self.assertGreater(q2["plasticity"], q3["plasticity"])
        self.assertLess(q2["integrity"], q3["integrity"])

    def test_adaptive_q2_and_q3_fail_in_different_directions(self):
        root = Path(__file__).resolve().parents[1]
        result = run_exp0006(root)
        q2_events = {row["event_id"]: row for row in result["arms"]["Adaptive-Q2"]["events"]}
        q3_events = {row["event_id"]: row for row in result["arms"]["Adaptive-Q3"]["events"]}

        self.assertFalse(q2_events["A1_correlated_echo"]["accepted"])
        self.assertTrue(q2_events["A2_two_origin_attack"]["accepted"])
        self.assertTrue(q2_events["G2_two_origin_novelty"]["accepted"])

        self.assertFalse(q3_events["A1_correlated_echo"]["accepted"])
        self.assertFalse(q3_events["A2_two_origin_attack"]["accepted"])
        self.assertFalse(q3_events["G2_two_origin_novelty"]["accepted"])

    def test_structural_validity_is_not_semantic_admissibility(self):
        root = Path(__file__).resolve().parents[1]
        result = run_exp0006(root)
        permissive_events = result["arms"]["Permissive"]["events"]
        attacks = [row for row in permissive_events if row["truth_effect"] == "pollution"]
        self.assertEqual(len(attacks), 2)
        self.assertTrue(all(row["structurally_valid"] for row in attacks))
        self.assertTrue(all(row["accepted"] for row in attacks))
        self.assertTrue(result["hypotheses"]["H6_structural_protocol_is_not_semantic_admissibility"])

    def test_supported_final_recovery_beats_rigid_staleness(self):
        root = Path(__file__).resolve().parents[1]
        result = run_exp0006(root)
        rigid = result["arms"]["Rigid"]["summary"]
        for arm in ("Permissive", "Adaptive-Q2", "Adaptive-Q3"):
            self.assertLess(result["arms"][arm]["summary"]["final_target_js"], rigid["final_target_js"])
        self.assertTrue(all(result["hypotheses"].values()))


if __name__ == "__main__":
    unittest.main()
