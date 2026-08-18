import unittest

from python.scl_exp.sci import build_sci_package
from python.scl_exp.persistent_cognition import CognitionState, restart_cognition


class PersistentCognitionTests(unittest.TestCase):
    def setUp(self):
        self.features = [f"F{i:02d}" for i in range(1, 20)]
        self.independent = build_sci_package("qevra", [0.25] * 19, self.features, "agent", top_k=19,
                                             provenance={"kind": "proposal"})
        self.corrected = build_sci_package("qevra", [0.8] * 18 + [0.01], self.features, "board", top_k=19,
                                           provenance={"kind": "correction"})

    def test_persistent_restart_restores_correction_and_history(self):
        state = CognitionState(
            agent="agent-A",
            independent_package=self.independent,
            active_package=self.corrected,
            version=2,
            accepted_hashes=[self.independent["sha256"], self.corrected["sha256"]],
            superseded_hashes=[self.independent["sha256"]],
            history=[{"event": "correction"}],
        )
        restarted = restart_cognition(state, persistent=True)
        self.assertEqual(restarted.active_package["sha256"], self.corrected["sha256"])
        self.assertEqual(restarted.version, 2)
        self.assertEqual(restarted.history, state.history)

    def test_nonpersistent_restart_returns_to_independent_and_empty_history(self):
        state = CognitionState(
            agent="agent-A",
            independent_package=self.independent,
            active_package=self.corrected,
            version=2,
            accepted_hashes=[self.independent["sha256"], self.corrected["sha256"]],
            superseded_hashes=[self.independent["sha256"]],
            history=[{"event": "correction"}],
        )
        restarted = restart_cognition(state, persistent=False)
        self.assertEqual(restarted.active_package["sha256"], self.independent["sha256"])
        self.assertEqual(restarted.version, 1)
        self.assertEqual(restarted.history, [])
        self.assertEqual(restarted.superseded_hashes, [])


if __name__ == "__main__":
    unittest.main()
