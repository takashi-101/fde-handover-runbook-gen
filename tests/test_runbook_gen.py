import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from runbook_gen import HandoverSpec, generate_runbook_markdown


def _spec(**overrides) -> HandoverSpec:
    fields = dict(
        system_name="架空システム",
        owner_role="架空課 運用担当",
        daily_commands=["python check.py"],
        escalation_contact="架空の担当窓口",
        rollback_steps=["機能を停止する"],
    )
    fields.update(overrides)
    return HandoverSpec(**fields)


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


# 正常系
class TestNormal(unittest.TestCase):
    def test_exact_output(self) -> None:
        spec = _spec(
            daily_commands=["python check.py", "python report.py --date today"],
            rollback_steps=["機能を停止する", "前日の設定に戻す"],
        )
        self.assertEqual(
            generate_runbook_markdown(spec),
            "# 運用引き継ぎ手順書：架空システム\n"
            "\n"
            "- **主管ロール**：架空課 運用担当\n"
            "- **異常時エスカレーション先**：架空の担当窓口\n"
            "\n"
            "## 1. 日次確認コマンド\n"
            "- `python check.py`\n"
            "- `python report.py --date today`\n"
            "\n"
            "## 2. 異常発生時の切り戻し手順\n"
            "1. 機能を停止する\n"
            "2. 前日の設定に戻す\n",
        )

    def test_commands_keep_input_order(self) -> None:
        md = generate_runbook_markdown(_spec(daily_commands=["c3", "c1", "c2"]))
        self.assertLess(md.index("- `c3`"), md.index("- `c1`"))
        self.assertLess(md.index("- `c1`"), md.index("- `c2`"))

    def test_rollback_steps_are_numbered_from_one(self) -> None:
        md = generate_runbook_markdown(_spec(rollback_steps=["a", "b", "c"]))
        self.assertIn("1. a\n2. b\n3. c\n", md)

    def test_output_ends_with_single_newline(self) -> None:
        md = generate_runbook_markdown(_spec())
        self.assertTrue(md.endswith("\n"))
        self.assertFalse(md.endswith("\n\n"))


# 境界値
class TestBoundary(unittest.TestCase):
    def test_empty_lists_leave_sections_empty(self) -> None:
        md = generate_runbook_markdown(_spec(daily_commands=[], rollback_steps=[]))
        self.assertIn("## 1. 日次確認コマンド\n\n\n## 2. 異常発生時の切り戻し手順\n\n", md)
        self.assertTrue(md.endswith("## 2. 異常発生時の切り戻し手順\n\n"))

    def test_empty_strings_are_not_rejected(self) -> None:
        md = generate_runbook_markdown(_spec(system_name="", owner_role="", escalation_contact=""))
        self.assertTrue(md.startswith("# 運用引き継ぎ手順書：\n"))
        self.assertIn("- **主管ロール**：\n", md)
        self.assertIn("- **異常時エスカレーション先**：\n", md)

    def test_markdown_symbols_are_not_escaped(self) -> None:
        md = generate_runbook_markdown(
            _spec(system_name="A*B_C", daily_commands=["echo `date`"], rollback_steps=["# 見出し"])
        )
        self.assertIn("# 運用引き継ぎ手順書：A*B_C\n", md)
        self.assertIn("- `echo `date``\n", md)
        self.assertIn("1. # 見出し\n", md)

    def test_newline_in_step_is_inserted_as_is(self) -> None:
        md = generate_runbook_markdown(_spec(rollback_steps=["1行目\n2行目"]))
        self.assertIn("1. 1行目\n2行目\n", md)

    def test_tuples_are_accepted(self) -> None:
        md = generate_runbook_markdown(_spec(daily_commands=("c1",), rollback_steps=("s1",)))
        self.assertIn("- `c1`\n", md)
        self.assertIn("1. s1\n", md)

    def test_spec_is_frozen(self) -> None:
        spec = _spec()
        with self.assertRaises(FrozenInstanceError):
            spec.system_name = "別名"  # type: ignore[misc]


# 異常系
class TestError(unittest.TestCase):
    def test_missing_field_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            HandoverSpec(system_name="架空システム", owner_role="架空課")  # type: ignore[call-arg]

    def test_unknown_field_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            _spec(memo="未定義の項目")

    def test_none_commands_raise_type_error(self) -> None:
        with self.assertRaises(TypeError):
            generate_runbook_markdown(_spec(daily_commands=None))

    def test_none_rollback_steps_raise_type_error(self) -> None:
        with self.assertRaises(TypeError):
            generate_runbook_markdown(_spec(rollback_steps=None))

    def test_dict_instead_of_spec_raises_attribute_error(self) -> None:
        with self.assertRaises(AttributeError):
            generate_runbook_markdown({"system_name": "架空システム"})  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
