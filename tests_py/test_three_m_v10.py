import json
import tempfile
from pathlib import Path

from python.scl_exp.exp0010 import run_exp0010
from python.scl_exp.three_m_v10 import export_three_m_v10, verify_three_m_v10


def test_v10_3m_export_is_repeatable_and_excludes_audit_sidecars():
    repo = Path(__file__).resolve().parents[1]
    result = run_exp0010(repo)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        export_three_m_v10(result, root)
        first = (root / "checksums.json").read_bytes()
        (root / "GITHUB_INDEX.json").write_text('{"audit":true}\n', encoding="utf-8")
        (root / "verification.json").write_text('{"old":true}\n', encoding="utf-8")
        export_three_m_v10(result, root)
        second = (root / "checksums.json").read_bytes()
        assert first == second
        checks = json.loads(second)
        assert "verification.json" not in checks
        assert "GITHUB_INDEX.json" not in checks
        verification = verify_three_m_v10(root)
        assert verification["valid"]
        assert verification["files_checked"] >= 9
