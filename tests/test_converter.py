import unittest
import tempfile
import shutil
from pathlib import Path

from src.converter.book_converter import BookConverter

class TestBookConverter(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.temp_dir) / "markdown"
        self.output_dir = Path(self.temp_dir) / "json"
        self.input_dir.mkdir(parents=True, exist_ok=True)

        # Create sample markdown file
        sample_md = self.input_dir / "test-book.md"
        with open(sample_md, "w", encoding="utf-8") as f:
            f.write("# Test Book\n\n# Chapter 1\n\n## Section 1.1\n\nHello World.")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_process_all(self):
        converter = BookConverter(input_dir=str(self.input_dir), output_dir=str(self.output_dir))
        res = converter.process_all()

        self.assertEqual(res["total_files"], 1)
        expected_json = self.output_dir / "test-book.json"
        self.assertTrue(expected_json.exists())

if __name__ == "__main__":
    unittest.main()
