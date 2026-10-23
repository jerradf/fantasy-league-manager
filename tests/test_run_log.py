import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from run_log import write_run_log


class TestRunLog(unittest.TestCase):
    def test_write_run_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_run_log(["hello log"], base_dir=tmp)
            self.assertTrue(path.exists())
            self.assertTrue(re.match(r"^\d{4}-\d{2}-\d{2}_\d{4}\.md$", path.name))
            text = path.read_text()
            self.assertTrue(text.startswith("# Run log"))
            self.assertIn("hello log", text)


if __name__ == "__main__":
    unittest.main()
