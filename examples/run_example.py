"""examples/sample_spec.json から HandoverSpec を作り、generate_runbook_markdown の出力を表示します。"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from runbook_gen import HandoverSpec, generate_runbook_markdown  # noqa: E402

SAMPLE = ROOT / "examples" / "sample_spec.json"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    spec = HandoverSpec(**json.loads(SAMPLE.read_text(encoding="utf-8")))
    sys.stdout.write(generate_runbook_markdown(spec))


if __name__ == "__main__":
    main()
