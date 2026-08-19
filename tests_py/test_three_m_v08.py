import json
import tempfile
import unittest
from pathlib import Path

from python.scl_exp.exp0008 import run_exp0008
from python.scl_exp.three_m_v08 import export_three_m_v08, verify_three_m_v08


class ThreeMV08Tests(unittest.TestCase):
    def test_export_is_repeatable_and_excludes_audit_sidecars(self):
        repo = Path(__file__).resolve().parents[1]
        result = run_exp0008(repo)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            export_three_m_v08(result, root)
            first = (root / 'checksums.json').read_bytes()
            (root / 'GITHUB_INDEX.json').write_text('{"audit":true}\n', encoding='utf-8')
            (root / 'verification.json').write_text('{"old":true}\n', encoding='utf-8')
            export_three_m_v08(result, root)
            second = (root / 'checksums.json').read_bytes()
            self.assertEqual(first, second)
            checks = json.loads(second)
            self.assertNotIn('GITHUB_INDEX.json', checks)
            self.assertNotIn('verification.json', checks)
            self.assertTrue(verify_three_m_v08(root)['valid'])


if __name__ == '__main__':
    unittest.main()
