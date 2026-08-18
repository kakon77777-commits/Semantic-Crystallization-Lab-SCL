import json
import tempfile
import unittest
from pathlib import Path

from python.scl_exp.exp0005 import run_exp0005
from python.scl_exp.three_m_v05 import export_three_m_v05, verify_three_m_v05


class ThreeMV05Tests(unittest.TestCase):
    def test_export_is_repeatable_and_excludes_verification_self_reference(self):
        repo = Path(__file__).resolve().parents[1]
        result = run_exp0005(repo)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            export_three_m_v05(result, root)
            first = (root / "checksums.json").read_bytes()
            (root / "verification.json").write_text('{"old":true}\n', encoding="utf-8")
            (root / "GITHUB_INDEX.json").write_text('{"audit":true}\n', encoding="utf-8")
            export_three_m_v05(result, root)
            second = (root / "checksums.json").read_bytes()
            self.assertEqual(first, second)
            checks = json.loads(second)
            self.assertNotIn("verification.json", checks)
            self.assertNotIn("checksums.json", checks)
            self.assertNotIn("GITHUB_INDEX.json", checks)
            verification = verify_three_m_v05(root)
            self.assertTrue(verification["valid"])
            self.assertGreaterEqual(verification["files_checked"], 8)


if __name__ == "__main__":
    unittest.main()
