import copy
import unittest

from python.scl_exp.sci import build_sci_package
from python.scl_exp.sci_protocol import (
    ProtocolState,
    build_envelope,
    process_protocol_batch,
    verify_envelope,
)


class SciProtocolTests(unittest.TestCase):
    def setUp(self):
        self.features = [f"F{i:02d}" for i in range(1, 20)]
        self.base = build_sci_package("qevra", [0.2] * 19, self.features, "agent-A", top_k=19,
                                      provenance={"kind": "proposal"})
        self.current = build_sci_package("qevra", [0.8] * 18 + [0.01], self.features, "board", top_k=19,
                                         provenance={"kind": "median-correction"})
        self.bad = build_sci_package("qevra", [0.1] * 18 + [0.95], self.features, "fault", top_k=19,
                                     provenance={"kind": "conflict"})

    def test_envelope_hash_verifies_and_tamper_fails(self):
        env = build_envelope(self.current, version=2, parent_sha256=self.base["sha256"], source_agent="board",
                             event_type="imprint.correction", provenance={"reason": "median"})
        self.assertTrue(verify_envelope(env))
        tampered = copy.deepcopy(env)
        tampered["version"] = 3
        self.assertFalse(verify_envelope(tampered))

    def test_missing_provenance_is_rejected(self):
        state = ProtocolState.from_package(self.base, version=1)
        env = build_envelope(self.current, version=2, parent_sha256=self.base["sha256"], source_agent="board",
                             event_type="imprint.correction", provenance={"reason": "median"})
        env["provenance"] = {}
        out = process_protocol_batch(state, [env])
        self.assertEqual(out.accepted, [])
        self.assertEqual(out.rejected[0]["reason"], "missing_provenance")
        self.assertEqual(out.state.active_package_sha256, self.base["sha256"])

    def test_stale_and_rollback_are_rejected_but_duplicate_is_idempotent(self):
        state = ProtocolState.from_package(self.current, version=2, superseded={self.base["sha256"]})
        duplicate = build_envelope(self.current, version=2, parent_sha256=self.base["sha256"], source_agent="board",
                                   event_type="imprint.correction", provenance={"reason": "repeat"})
        stale = build_envelope(self.base, version=1, parent_sha256=None, source_agent="agent-A",
                               event_type="imprint.proposal", provenance={"reason": "old"})
        rollback = build_envelope(self.base, version=3, parent_sha256=self.current["sha256"], source_agent="agent-A",
                                  event_type="imprint.correction", provenance={"reason": "rollback", "operation": "rollback"})
        out = process_protocol_batch(state, [duplicate, stale, rollback])
        self.assertEqual(len(out.accepted), 1)
        self.assertEqual(out.accepted[0]["status"], "idempotent")
        reasons = {row["reason"] for row in out.rejected}
        self.assertIn("stale_version", reasons)
        self.assertIn("rollback_to_superseded", reasons)
        self.assertEqual(out.state.active_package_sha256, self.current["sha256"])

    def test_same_version_same_parent_fork_is_quarantined(self):
        state = ProtocolState.from_package(self.current, version=2, superseded={self.base["sha256"]})
        a = build_envelope(self.current, version=3, parent_sha256=self.current["sha256"], source_agent="agent-B",
                           event_type="imprint.correction", provenance={"reason": "reaffirm"})
        b = build_envelope(self.bad, version=3, parent_sha256=self.current["sha256"], source_agent="agent-C",
                           event_type="imprint.correction", provenance={"reason": "conflict"})
        out = process_protocol_batch(state, [a, b])
        self.assertEqual(out.accepted, [])
        self.assertEqual(len(out.rejected), 2)
        self.assertTrue(all(row["reason"] == "conflicting_correction" for row in out.rejected))
        self.assertEqual(out.state.active_package_sha256, self.current["sha256"])


if __name__ == "__main__":
    unittest.main()
