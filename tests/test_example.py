import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _lines(text: str) -> list:
    return [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]


class TestExample(unittest.TestCase):
    def test_readme_shows_actual_output_of_sample_run(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "examples" / "run_example.py")],
            capture_output=True,
            check=True,
        )
        output = _lines(proc.stdout.decode("utf-8"))
        while output and output[-1] == "":
            output.pop()
        readme = _lines((ROOT / "README.md").read_text(encoding="utf-8"))
        n = len(output)
        found = any(readme[i : i + n] == output for i in range(len(readme) - n + 1))
        self.assertTrue(found, "README does not contain the actual output of examples/run_example.py")


if __name__ == "__main__":
    unittest.main()
