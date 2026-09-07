import unittest
import tempfile
from pathlib import Path

from src.parser.block_parser import parse_block
from src.parser.md_parser import MarkdownParser
from src.models.content import CodeNode, TableNode, ListNode, NoteNode, WarningNode, ParagraphNode

class TestBlockParser(unittest.TestCase):

    def test_parse_code_block(self):
        block = "```python\ndef hello():\n    print('Hello World')\n```"
        node = parse_block(block)
        self.assertIsInstance(node, CodeNode)
        self.assertEqual(node.language, "python")
        self.assertEqual(node.code, "def hello():\n    print('Hello World')")

    def test_parse_table(self):
        block = "| Header 1 | Header 2 |\n| --- | --- |\n| Cell 1 | Cell 2 |"
        node = parse_block(block)
        self.assertIsInstance(node, TableNode)
        self.assertEqual(node.headers, ["Header 1", "Header 2"])
        self.assertEqual(node.rows, [["Cell 1", "Cell 2"]])

    def test_parse_unordered_list(self):
        block = "- Item 1\n- Item 2\n- Item 3"
        node = parse_block(block)
        self.assertIsInstance(node, ListNode)
        self.assertFalse(node.ordered)
        self.assertEqual(node.items, ["Item 1", "Item 2", "Item 3"])

    def test_parse_note_callout(self):
        block = "> **Note:** This operation is expensive."
        node = parse_block(block)
        self.assertIsInstance(node, NoteNode)
        self.assertEqual(node.text, "This operation is expensive.")

class TestMarkdownParser(unittest.TestCase):

    def test_parse_document_hierarchy(self):
        md_content = """# Sample Book Title

# Chapter 1: Introduction

## What is Clean Code?

Pointers store memory addresses.

```cpp
#include <iostream>

int main() {
    std::cout << "Hello";
}
```

### Sub-Topic

Details here.
"""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(md_content)
            temp_path = f.name

        try:
            parser = MarkdownParser(temp_path)
            book, warnings = parser.parse()
            book_dict = book.to_dict()

            self.assertEqual(book_dict["book"]["total_chapters"], 1)
            self.assertEqual(len(book_dict["chapters"]), 1)
            chap = book_dict["chapters"][0]
            self.assertEqual(chap["title"], "Introduction")
            self.assertTrue(len(chap["sections"]) >= 1)
        finally:
            Path(temp_path).unlink(missing_ok=True)

if __name__ == "__main__":
    unittest.main()
