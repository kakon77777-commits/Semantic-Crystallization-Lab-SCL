import unittest

from python.scl_exp.adaptive_admission import AdaptiveAdmissionConfig, AdaptiveAdmissionPolicy, RootTrustLedger


class AdaptiveAdmissionTests(unittest.TestCase):
    def test_correlated_aliases_count_as_one_origin(self):
        policy = AdaptiveAdmissionPolicy(AdaptiveAdmissionConfig(min_distinct_origins=2))
        evidence = [
            {"source_agent": "alias-a", "origin_root": "shared-root"},
            {"source_agent": "alias-b", "origin_root": "shared-root"},
            {"source_agent": "alias-c", "origin_root": "shared-root"},
        ]
        decision = policy.decide(evidence, risk=0.1, novelty_js=0.0)
        self.assertFalse(decision.accepted)
        self.assertEqual(decision.distinct_origins, 1)
        self.assertEqual(decision.reason, "insufficient_independent_origins")

    def test_delayed_feedback_moves_root_reliability(self):
        ledger = RootTrustLedger(alpha0=2.0, beta0=2.0)
        self.assertAlmostEqual(ledger.mean("root-a"), 0.5)
        ledger.observe(["root-a"], genuine=True)
        self.assertGreater(ledger.mean("root-a"), 0.5)
        before_bad = ledger.mean("root-b")
        ledger.observe(["root-b"], genuine=False)
        self.assertLess(ledger.mean("root-b"), before_bad)

    def test_required_support_rises_with_risk_and_recent_pollution(self):
        policy = AdaptiveAdmissionPolicy(AdaptiveAdmissionConfig())
        low = policy.required_support(risk=0.1, novelty_js=0.005)
        high = policy.required_support(risk=0.9, novelty_js=0.005)
        self.assertGreater(high, low)
        policy.observe_feedback(["root-x"], genuine=False)
        hostile = policy.required_support(risk=0.1, novelty_js=0.005)
        self.assertGreater(hostile, low)

    def test_two_trusted_origins_can_pass_where_two_distrusted_origins_fail(self):
        policy = AdaptiveAdmissionPolicy(AdaptiveAdmissionConfig())
        for _ in range(5):
            policy.observe_feedback(["good-a", "good-b"], genuine=True)
            policy.observe_feedback(["bad-a", "bad-b"], genuine=False)
        good = policy.decide(
            [{"source_agent": "ga", "origin_root": "good-a"}, {"source_agent": "gb", "origin_root": "good-b"}],
            risk=0.55,
            novelty_js=0.01,
        )
        bad = policy.decide(
            [{"source_agent": "ba", "origin_root": "bad-a"}, {"source_agent": "bb", "origin_root": "bad-b"}],
            risk=0.55,
            novelty_js=0.01,
        )
        self.assertTrue(good.accepted)
        self.assertFalse(bad.accepted)
        self.assertGreater(good.effective_support, bad.effective_support)


if __name__ == "__main__":
    unittest.main()
