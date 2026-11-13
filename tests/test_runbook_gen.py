import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from runbook_gen import HandoverSpec, generate_runbook_markdown


class TestRunbookGen(unittest.TestCase):
    def test_generates_complete_markdown_runbook(self) -> None:
        spec = HandoverSpec(
            system_name="窓口照会支援ツール",
            owner_role="庶務課 業務担当",
            daily_commands=["python3 -m ops_doctor.checker"],
            escalation_contact="情報システム担当窓口",
            rollback_steps=["AI連携フラグをOFFにする", "スプレッドシート手入力へ戻す"],
        )
        md = generate_runbook_markdown(spec)
        self.assertIn("# 運用引き継ぎ手順書：窓口照会支援ツール", md)
        self.assertIn("AI連携フラグをOFFにする", md)


if __name__ == "__main__":
    unittest.main()
