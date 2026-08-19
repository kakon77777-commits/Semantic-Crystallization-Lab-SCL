import unittest

from python.scl_exp.trust_dynamics import TrustAdmissionConfig, TrustDynamicsAdmissionPolicy, TrustDynamicsConfig


class TrustDynamicsAdmissionTests(unittest.TestCase):
    def test_decision_depends_on_history_risk_novelty_and_origins_not_truth_label(self):
        cfg = TrustAdmissionConfig(dynamics=TrustDynamicsConfig())
        policy_a = TrustDynamicsAdmissionPolicy('adaptive', cfg)
        policy_b = TrustDynamicsAdmissionPolicy('adaptive', cfg)
        evidence = [{'source_agent': 'a1', 'origin_root': 'A'}, {'source_agent': 'd1', 'origin_root': 'D'}]
        for policy in (policy_a, policy_b):
            policy.start_event(); policy.observe_delayed_feedback(['A'], genuine=True)
        self.assertEqual(policy_a.decide(evidence, risk=0.4, novelty_js=0.01), policy_b.decide(evidence, risk=0.4, novelty_js=0.01))

    def test_all_modes_share_the_same_required_support_formula(self):
        cfg = TrustAdmissionConfig(dynamics=TrustDynamicsConfig())
        policies = [TrustDynamicsAdmissionPolicy(mode, cfg) for mode in ('cumulative', 'fixed', 'adaptive')]
        required = [p.required_support(risk=0.7, novelty_js=0.02) for p in policies]
        self.assertEqual(len(set(round(x, 12) for x in required)), 1)

    def test_feedback_updates_recent_pollution_and_trust_only_after_decision_boundary(self):
        cfg = TrustAdmissionConfig(dynamics=TrustDynamicsConfig(), recent_window=3)
        policy = TrustDynamicsAdmissionPolicy('adaptive', cfg)
        before = policy.trust.mean('B')
        decision = policy.decide([{'source_agent': 'b1', 'origin_root': 'B'}, {'source_agent': 'c1', 'origin_root': 'C'}], risk=0.2, novelty_js=0.0)
        self.assertAlmostEqual(policy.trust.mean('B'), before)
        self.assertEqual(policy.recent_pollution_rate, 0.0)
        policy.start_event(); policy.observe_delayed_feedback(['B', 'C'], genuine=False)
        self.assertLess(policy.trust.mean('B'), before)
        self.assertGreater(policy.recent_pollution_rate, 0.0)
        self.assertIsInstance(decision.accepted, bool)


if __name__ == '__main__':
    unittest.main()
