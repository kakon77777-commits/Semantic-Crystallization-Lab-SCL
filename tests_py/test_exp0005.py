import unittest
from pathlib import Path

from python.scl_exp.exp0005 import run_exp0005


class Exp0005Tests(unittest.TestCase):
    def test_factorial_protocol_persistence_continuity(self):
        root = Path(__file__).resolve().parents[1]
        result = run_exp0005(root)
        self.assertEqual(set(result["arms"]), {"A00", "A01", "A10", "A11"})
        self.assertTrue(all(result["hypotheses"].values()))

        a00 = result["arms"]["A00"]["summary"]
        a01 = result["arms"]["A01"]["summary"]
        a10 = result["arms"]["A10"]["summary"]
        a11 = result["arms"]["A11"]["summary"]

        self.assertGreater(a00["mean_restart_js"], a01["mean_restart_js"])
        self.assertGreater(a10["mean_restart_js"], a11["mean_restart_js"])
        self.assertEqual(a01["prebootstrap_correction_retention"], 1.0)
        self.assertEqual(a10["prebootstrap_correction_retention"], 0.0)
        self.assertEqual(a00["final_correction_retention"], 0.0)
        self.assertEqual(a01["final_correction_retention"], 0.0)
        self.assertEqual(a10["final_correction_retention"], 1.0)
        self.assertEqual(a11["final_correction_retention"], 1.0)
        self.assertGreater(a00["mean_final_target_js"], a10["mean_final_target_js"])
        self.assertLess(a00["final_cross_agent_js"], 1e-12)
        self.assertLess(a10["final_cross_agent_js"], 1e-12)

    def test_protocol_fault_reasons_are_auditable(self):
        root = Path(__file__).resolve().parents[1]
        result = run_exp0005(root)
        for arm in ("A10", "A11"):
            reasons = result["arms"][arm]["summary"]["protocol_rejection_reasons"]
            self.assertGreaterEqual(reasons.get("stale_version", 0), 3)
            self.assertGreaterEqual(reasons.get("missing_provenance", 0), 3)
            self.assertGreaterEqual(reasons.get("rollback_to_superseded", 0), 3)
            self.assertGreaterEqual(reasons.get("conflicting_correction", 0), 6)


if __name__ == "__main__":
    unittest.main()
