import unittest

from python.scl_exp.sci import build_sci_package
from python.scl_exp.cognitive_transition import (
    TransitionPolicy,
    TransitionState,
    build_transition_request,
    process_transition,
)


class CognitiveTransitionLawTests(unittest.TestCase):
    def setUp(self):
        self.features = [f"F{i:02d}" for i in range(1, 6)]
        self.base = build_sci_package(
            "qevra", [0.50, 0.50, 0.50, 0.50, 0.00], self.features, "baseline", top_k=5,
            provenance={"kind": "accepted"},
        )
        self.genuine = build_sci_package(
            "qevra", [0.62, 0.58, 0.54, 0.66, 0.00], self.features, "candidate", top_k=5,
            provenance={"kind": "genuine-shift"},
        )
        self.polluted = build_sci_package(
            "qevra", [0.30, 0.32, 0.52, 0.34, 0.55], self.features, "candidate", top_k=5,
            provenance={"kind": "pollution"},
        )

    def evidence(self, target, roots):
        rows = []
        base = [target["weights"][fid] for fid in self.features]
        deltas = [0.012, -0.012, 0.0]
        for i, root in enumerate(roots):
            values = [min(1.0, max(0.0, v + (deltas[i % 3] if j % 2 == 0 else -deltas[i % 3]))) for j, v in enumerate(base)]
            pkg = build_sci_package(
                "qevra", values, self.features, f"observer-{i}", top_k=5,
                provenance={"observation": i, "origin_root": root},
            )
            rows.append({"source_agent": f"observer-{i}", "origin_root": root, "package": pkg})
        return rows

    def state(self):
        return TransitionState(symbol="qevra", active_package=self.base, generation=2)

    def request(self, state, candidate, label="shift"):
        return build_transition_request(
            state,
            candidate,
            source_agent="board",
            event_type="imprint.correction",
            provenance={"reason": label},
        )

    def test_rigid_rejects_even_well_supported_genuine_change(self):
        state = self.state()
        request = self.request(state, self.genuine)
        out = process_transition(state, request, self.evidence(self.genuine, ["r1", "r2", "r3"]), TransitionPolicy.rigid(), self.features)
        self.assertFalse(out.accepted)
        self.assertEqual(out.reason, "rigid_semantic_lock")
        self.assertEqual(out.state.active_package["sha256"], self.base["sha256"])

    def test_permissive_accepts_structurally_valid_correlated_pollution_after_first_evidence(self):
        state = self.state()
        request = self.request(state, self.polluted, "authorized-update")
        out = process_transition(state, request, self.evidence(self.polluted, ["same-root", "same-root", "same-root"]), TransitionPolicy.permissive(), self.features)
        self.assertTrue(out.accepted)
        self.assertEqual(out.evidence_consumed, 1)
        self.assertEqual(out.state.active_package["sha256"], self.polluted["sha256"])

    def test_adaptive_q2_accepts_two_origin_novelty_but_rejects_one_origin_echo(self):
        q2 = TransitionPolicy.adaptive(quorum=2)
        state = self.state()
        genuine_out = process_transition(state, self.request(state, self.genuine), self.evidence(self.genuine, ["r1", "r2"]), q2, self.features)
        self.assertTrue(genuine_out.accepted)
        self.assertEqual(genuine_out.evidence_consumed, 2)

        state2 = self.state()
        polluted_out = process_transition(state2, self.request(state2, self.polluted), self.evidence(self.polluted, ["echo", "echo", "echo"]), q2, self.features)
        self.assertFalse(polluted_out.accepted)
        self.assertEqual(polluted_out.reason, "insufficient_independent_evidence")

    def test_adaptive_q3_rejects_two_origin_novelty_and_two_origin_coordinated_pollution(self):
        q3 = TransitionPolicy.adaptive(quorum=3)
        for candidate, label in ((self.genuine, "genuine"), (self.polluted, "attack")):
            state = self.state()
            out = process_transition(state, self.request(state, candidate, label), self.evidence(candidate, ["r1", "r2"]), q3, self.features)
            self.assertFalse(out.accepted)
            self.assertEqual(out.reason, "insufficient_independent_evidence")


if __name__ == "__main__":
    unittest.main()
