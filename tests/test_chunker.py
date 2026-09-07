import unittest
import tempfile
import json
from pathlib import Path

from src.config import ChunkerConfig
from src.chunker.code_detector import CodeDetector
from src.chunker.normalizer import SchemaNormalizer
from src.chunker.structure import DocumentTraverser
from src.chunker.semantic_chunker import SemanticChunker, estimate_tokens
from src.chunker.validator import ChunkerValidator

class TestCodeDetector(unittest.TestCase):

    def test_cpp_code_detection(self):
        code_str = "#include <iostream>\nint main() {\n    std::cout << \"Hello World\";\n    return 0;\n}"
        self.assertTrue(CodeDetector.is_code(code_str))
        self.assertEqual(CodeDetector.detect_language(code_str), "cpp")

    def test_python_code_detection(self):
        code_str = "def process_data(items):\n    return [x * 2 for x in items]"
        self.assertTrue(CodeDetector.is_code(code_str))
        self.assertEqual(CodeDetector.detect_language(code_str), "python")

    def test_plain_text_not_code(self):
        text = "A pointer is a variable that stores the memory address of another variable."
        self.assertFalse(CodeDetector.is_code(text))


class TestSemanticChunker(unittest.TestCase):

    def test_token_estimation(self):
        text = "One two three four five"
        tokens = estimate_tokens(text)
        self.assertTrue(tokens >= 5)

    def test_chunking_structural_blocks(self):
        sample_book = {
            "book": {
                "id": "sample-book",
                "title": "Sample Book",
                "source_file": "sample.json"
            },
            "chapters": [
                {
                    "id": "chapter-01",
                    "number": 1,
                    "title": "Pointers",
                    "sections": [
                        {
                            "id": "chapter-01-sec-01",
                            "title": "Pointer Basics",
                            "level": 2,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "text": "A pointer is a variable that stores the memory address of another variable."
                                },
                                {
                                    "type": "code",
                                    "language": "cpp",
                                    "code": "int x = 10;\nint *p = &x;"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        norm_data = SchemaNormalizer.normalize_book(sample_book)
        blocks = DocumentTraverser.extract_blocks(norm_data)
        config = ChunkerConfig(chunk_size=500, chunk_overlap=50)
        chunker = SemanticChunker(config)
        chunks = chunker.chunk_blocks(blocks)

        self.assertTrue(len(chunks) >= 1)
        stats = ChunkerValidator.validate_chunks(chunks)
        self.assertEqual(stats["errors_count"], 0)


if __name__ == "__main__":
    unittest.main()
