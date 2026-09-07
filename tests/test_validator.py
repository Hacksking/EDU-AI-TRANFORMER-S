import unittest
from src.validator.json_validator import JSONValidator

class TestJSONValidator(unittest.TestCase):

    def test_valid_json_structure(self):
        sample_data = {
            "book": {
                "id": "sample-book",
                "title": "Sample Book",
                "authors": ["Author"],
                "description": None,
                "source_file": "sample.md",
                "language": "en",
                "total_chapters": 1
            },
            "chapters": [
                {
                    "id": "chapter-01",
                    "number": 1,
                    "title": "Introduction",
                    "sections": [
                        {
                            "id": "chapter-01-section-01",
                            "title": "Getting Started",
                            "level": 2,
                            "content": [
                                {"type": "paragraph", "text": "Hello world"},
                                {"type": "code", "language": "python", "code": "print('hello')"}
                            ]
                        }
                    ],
                    "source": {
                        "file": "sample.md",
                        "chapter": 1,
                        "heading": "Introduction",
                        "line_start": 1,
                        "line_end": 20
                    }
                }
            ]
        }

        stats = JSONValidator.validate_dict(sample_data)
        self.assertTrue(stats["success"])
        self.assertEqual(stats["chapters"], 1)
        self.assertEqual(stats["sections"], 1)
        self.assertEqual(stats["code_blocks"], 1)
        self.assertEqual(stats["warnings_count"], 0)

    def test_missing_top_level_keys(self):
        sample_data = {"book": {}}
        stats = JSONValidator.validate_dict(sample_data)
        self.assertFalse(stats["success"])
        self.assertTrue(any("chapters" in w for w in stats["warnings"]))

if __name__ == "__main__":
    unittest.main()
