import unittest

from python.scl_exp.trust_dynamics import TrustDynamicsLedger, TrustDynamicsConfig


class TrustDynamicsTests(unittest.TestCase):
    def test_fixed_and_adaptive_decay_move_stale_evidence_toward_prior(self):
        cfg = TrustDynamicsConfig(fixed_decay=0.8, adaptive_base_decay=0.9)
        cumulative = TrustDynamicsLedger('cumulative', cfg)
        fixed = TrustDynamicsLedger('fixed', cfg)
        adaptive = TrustDynamicsLedger('adaptive', cfg)
        for ledger in (cumulative, fixed, adaptive):
            for _ in range(4):
                ledger.observe(['A'], genuine=True)
        before = {name: ledger.mean('A') for name, ledger in [('c', cumulative), ('f', fixed), ('a', adaptive)]}
        for ledger in (cumulative, fixed, adaptive):
            ledger.advance(); ledger.advance()
        self.assertAlmostEqual(cumulative.mean('A'), before['c'])
        self.assertLess(fixed.mean('A'), before['f'])
        self.assertLess(adaptive.mean('A'), before['a'])
        self.assertGreater(fixed.mean('A'), 0.5)
        self.assertGreater(adaptive.mean('A'), 0.5)

    def test_adaptive_betrayal_penalizes_high_reputation_faster_than_fixed(self):
        cfg = TrustDynamicsConfig(fixed_decay=0.95, betrayal_boost=2.5)
        fixed = TrustDynamicsLedger('fixed', cfg)
        adaptive = TrustDynamicsLedger('adaptive', cfg)
        for ledger in (fixed, adaptive):
            for _ in range(6): ledger.observe(['B'], genuine=True)
            ledger.advance()
        fixed.observe(['B'], genuine=False); adaptive.observe(['B'], genuine=False)
        self.assertLess(adaptive.mean('B'), fixed.mean('B'))
        self.assertGreater(adaptive.volatility('B'), fixed.volatility('B'))

    def test_adaptive_recovery_can_rehabilitate_low_reputation_source_faster(self):
        cfg = TrustDynamicsConfig(fixed_decay=0.95, recovery_boost=2.0)
        fixed = TrustDynamicsLedger('fixed', cfg)
        adaptive = TrustDynamicsLedger('adaptive', cfg)
        for ledger in (fixed, adaptive):
            for _ in range(5): ledger.observe(['C'], genuine=False)
            ledger.advance()
        self.assertLess(adaptive.mean('C'), 0.5)
        self.assertLess(fixed.mean('C'), 0.5)
        fixed.observe(['C'], genuine=True); adaptive.observe(['C'], genuine=True)
        self.assertGreater(adaptive.mean('C') - 0.5, fixed.mean('C') - 0.5)


if __name__ == '__main__':
    unittest.main()
