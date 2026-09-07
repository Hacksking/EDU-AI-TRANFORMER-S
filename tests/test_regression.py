import unittest

from src.chunker.normalizer import SchemaNormalizer
from src.chunker.structure import DocumentTraverser
from src.chunker.semantic_chunker import SemanticChunker
from src.config import ChunkerConfig

class TestRegression(unittest.TestCase):

    def test_fake_code_heading_demotion(self):
        """Tests that 'int s = sum(a, 4);' is NOT treated as a heading and is demoted to a code content node."""
        title = "int s = sum(a, 4);"
        self.assertTrue(SchemaNormalizer.is_fake_code_heading(title))

        sample_book = {
            "book": {
                "id": "beej-guide",
                "title": "Beej's Guide to C",
                "source_file": "beej.json"
            },
            "chapters": [
                {
                    "id": "chapter-32",
                    "number": 32,
                    "title": "Unnamed Objects",
                    "sections": [
                        {
                            "id": "chapter-32-sec-01",
                            "title": "Section 32.1",
                            "level": 2,
                            "sections": [
                                {
                                    "id": "fake-sec-id",
                                    "title": "int s = sum(a, 4);",
                                    "level": 3,
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "text": "Check it out—we are replacing the variable."
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        norm_data = SchemaNormalizer.normalize_book(sample_book)
        
        # Verify that the fake section title was demoted and removed from sections list
        sec = norm_data["chapters"][0]["sections"][0]
        self.assertEqual(len(sec.get("sections", [])), 0)
        
        # Verify that code node was added to section content
        content_nodes = sec["content"]
        types = [n["type"] for n in content_nodes]
        self.assertIn("code", types)
        
        code_node = next(n for n in content_nodes if n["type"] == "code")
        self.assertEqual(code_node["code"], "int s = sum(a, 4);")

        # Verify semantic chunk output
        blocks = DocumentTraverser.extract_blocks(norm_data)
        chunker = SemanticChunker(ChunkerConfig())
        chunks = chunker.chunk_blocks(blocks)
        
        code_chunks = [c for c in chunks if c["content_type"] == "code" or "int s = sum(a, 4);" in c["content"]]
        self.assertTrue(len(code_chunks) >= 1)
        self.assertNotEqual(code_chunks[0]["section"]["title"], "int s = sum(a, 4);")


if __name__ == "__main__":
    unittest.main()
