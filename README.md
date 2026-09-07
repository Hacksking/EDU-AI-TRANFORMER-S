# Markdown → Structured JSON Converter Pipeline

A deterministic, lossless **Markdown to Structured JSON parsing pipeline** designed to parse technical books into rich, traceable JSON representations for downstream RAG, semantic chunking, and vector database ingestion.

---

## Features

- **100% Deterministic**: No LLM calls or random UUID generation. Running twice on the same Markdown yields identical structures and stable IDs.
- **Lossless Content Preservation**: Preserves code blocks, tables, images, lists, callouts, and paragraphs without modification or summarization.
- **Heading Hierarchy**: Preserves nested section hierarchy (`##`, `###`, `####`) without flattening.
- **Source Traceability**: Every chapter and section tracks `file`, `chapter`, `heading`, `line_start`, and `line_end`.
- **Validation Pipeline**: Automated schema validation, duplicate ID checking, and element preservation auditing.
- **Read-Only Source Guarantee**: The source `markdown/` directory is never modified.

---

## Directory Structure

```text
project/
├── markdown/          # Input folder containing Markdown books
├── json/              # Output folder for generated JSON files
├── src/
│   ├── models/        # Data classes for Book, Chapter, Section, Content Nodes
│   ├── parser/        # Markdown block tokenizer & document hierarchy builder
│   ├── converter/     # Pipeline orchestrator
│   ├── validator/     # JSON schema and integrity validator
│   └── utils/         # Slugifier, ID generator, & terminal reporter
├── tests/             # Unit and integration test suite
├── main.py            # CLI entrypoint
├── README.md          # Project documentation
└── requirements.txt   # Project dependencies
```

---

## Quick Start

### Basic Usage

Run the converter pipeline with default input (`markdown/`) and output (`json/`):

```bash
python main.py
```

### Custom Directories

Specify custom input and output folders:

```bash
python main.py --input markdown --output json
```

---

## JSON Output Specification

Each generated JSON file follows this structure:

```json
{
  "book": {
    "id": "clean-code",
    "title": "Clean Code",
    "authors": [],
    "description": null,
    "source_file": "clean-code.md",
    "language": "en",
    "total_chapters": 17
  },
  "chapters": [
    {
      "id": "chapter-01",
      "number": 1,
      "title": "Introduction",
      "sections": [
        {
          "id": "chapter-01-section-01-what-is-clean-code",
          "title": "What is Clean Code?",
          "level": 2,
          "content": [
            {
              "type": "paragraph",
              "text": "Pointers store memory addresses."
            },
            {
              "type": "code",
              "language": "cpp",
              "code": "#include <iostream>\n\nint main() {\n    std::cout << \"Hello\";\n}"
            }
          ]
        }
      ],
      "source": {
        "file": "clean-code.md",
        "chapter": 1,
        "heading": "Introduction",
        "line_start": 1,
        "line_end": 145
      }
    }
  ]
}
```

---

## Supported Content Types

| Content Type | JSON `type` | Preserved Fields |
|---|---|---|
| Paragraph | `paragraph` | `text` |
| Code Block | `code` | `language`, `code` (indentation & comments untouched) |
| Heading | `heading` | `level`, `text` |
| List | `list` | `ordered` (boolean), `items` (array) |
| Quote | `quote` | `text` |
| Table | `table` | `headers` (array), `rows` (2D array) |
| Image | `image` | `alt`, `src` |
| Link | `link` | `text`, `url` |
| Note | `note` | `text` |
| Warning | `warning` | `text` |
| Raw Fallback | `raw` | `text` (fallback for unparseable syntax) |

---

## Running Tests

Execute the unit test suite:

```bash
python -m unittest discover -s tests -p "test_*.py"
```
