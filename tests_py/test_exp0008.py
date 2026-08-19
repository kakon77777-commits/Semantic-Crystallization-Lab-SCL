import unittest
from pathlib import Path

from python.scl_exp.exp0008 import run_exp0008


class Exp0008Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.result = run_exp0008(cls.repo)

    def test_expected_policy_arms_and_online_sequence_exist(self):
        self.assertEqual(set(self.result['arms']), {'Cumulative-History', 'Fixed-Decay', 'Adaptive-Dynamics', 'Oracle'})
        self.assertGreaterEqual(len(self.result['event_fixtures']), 20)
        self.assertEqual(self.result['boundaries']['feedback_mode'], 'one_event_delayed')
        self.assertFalse(self.result['boundaries']['current_truth_visible_to_policy'])

    def test_adaptive_records_time_varying_trust_and_volatility(self):
        arm = self.result['arms']['Adaptive-Dynamics']
        self.assertGreater(len(arm['trust_trajectory']), 0)
        b_values = [row['trust'].get('B', {}).get('mean') for row in arm['trust_trajectory'] if 'B' in row['trust']]
        self.assertGreater(max(b_values) - min(b_values), 0.15)
        vol = [row['trust'].get('B', {}).get('volatility', 0.0) for row in arm['trust_trajectory'] if 'B' in row['trust']]
        self.assertGreater(max(vol), 0.0)

    def test_oracle_is_only_evaluation_ceiling(self):
        oracle = self.result['arms']['Oracle']['summary']
        self.assertEqual(oracle['false_accept_rate'], 0.0)
        self.assertEqual(oracle['false_reject_rate'], 0.0)
        self.assertEqual(oracle['risk_weighted_cumulative_target_js'], 0.0)


if __name__ == '__main__':
    unittest.main()
