"""Generates standardized operational handover runbooks in Markdown."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class HandoverSpec:
    system_name: str
    owner_role: str
    daily_commands: List[str]
    escalation_contact: str
    rollback_steps: List[str]


def generate_runbook_markdown(spec: HandoverSpec) -> str:
    cmds = "\n".join(f"- `{c}`" for c in spec.daily_commands)
    rb = "\n".join(f"{i}. {s}" for i, s in enumerate(spec.rollback_steps, start=1))
    return (
        f"# 運用引き継ぎ手順書：{spec.system_name}\n\n"
        f"- **主管ロール**：{spec.owner_role}\n"
        f"- **異常時エスカレーション先**：{spec.escalation_contact}\n\n"
        f"## 1. 日次確認コマンド\n{cmds}\n\n"
        f"## 2. 異常発生時の切り戻し手順\n{rb}\n"
    )
