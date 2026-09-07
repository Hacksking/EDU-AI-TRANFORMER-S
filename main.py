import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any

from src.config import ChunkerConfig
from src.chunker.loader import JSONLoader
from src.chunker.normalizer import SchemaNormalizer
from src.chunker.structure import DocumentTraverser
from src.chunker.semantic_chunker import SemanticChunker
from src.chunker.validator import ChunkerValidator
from src.chunker.writer import JSONLWriter
from src.converter.book_converter import BookConverter

def run_chunker_pipeline(config: ChunkerConfig, validate_only: bool = False):
    loader = JSONLoader(logs_dir=str(config.logs_dir))
    files = loader.discover_files(config.input_dir)

    if not files:
        print(f"No JSON files found in '{config.input_dir}'.")
        return

    print("=" * 65)
    print("JSON -> SEMANTIC CHUNKING PIPELINE (.jsonl)")
    print("=" * 65)
    print(f"Input Directory:  {config.input_dir}")
    print(f"Output Directory: {config.output_dir}")
    print(f"Target Chunk Size:{config.chunk_size} tokens")
    print(f"Chunk Overlap:    {config.chunk_overlap} tokens")
    print(f"Found {len(files)} JSON file(s) to process.\n")

    chunker = SemanticChunker(config)

    total_books = 0
    total_chunks = 0
    total_text = 0
    total_code = 0
    total_mixed = 0
    total_table = 0
    total_other = 0
    total_warnings = 0
    total_errors = 0

    for idx, json_file in enumerate(files, start=1):
        raw_data = loader.load_file(json_file)
        if raw_data is None:
            total_errors += 1
            continue

        total_books += 1

        # 1. Normalize schema and demote fake headings
        norm_data = SchemaNormalizer.normalize_book(raw_data)

        # 2. Extract structural blocks
        blocks = DocumentTraverser.extract_blocks(norm_data)

        # 3. Generate semantic chunks
        file_chunks = chunker.chunk_blocks(blocks)

        # 4. Validate chunks
        stats = ChunkerValidator.validate_chunks(file_chunks)

        # 5. Write to .jsonl
        jsonl_filename = json_file.stem + ".jsonl"
        output_jsonl_path = config.output_dir / jsonl_filename

        if not validate_only:
            JSONLWriter.write_jsonl(file_chunks, output_jsonl_path)

        total_chunks += stats["total_chunks"]
        total_text += stats["text"]
        total_code += stats["code"]
        total_mixed += stats["mixed"]
        total_table += stats["table"]
        total_other += stats["other"]
        total_warnings += stats["warnings_count"]
        total_errors += stats["errors_count"]

        status_str = "[VALIDATED]" if validate_only else "[OK]"
        print(f"[{idx}/{len(files)}] {json_file.name}")
        print(f"      {status_str} Chunks: {stats['total_chunks']} (Text: {stats['text']}, Code: {stats['code']}, Mixed: {stats['mixed']}, Table: {stats['table']})")
        if not validate_only:
            print(f"      -> chunks/{jsonl_filename}")
        print()

    print("=" * 65)
    print("CHUNKING PIPELINE SUMMARY")
    print("=" * 65)
    print(f"Books processed:  {total_books}")
    print(f"Chunks generated: {total_chunks}\n")
    print(f"Text chunks:      {total_text}")
    print(f"Code chunks:      {total_code}")
    print(f"Mixed chunks:     {total_mixed}")
    print(f"Table chunks:     {total_table}")
    print(f"Other:            {total_other}\n")
    print(f"Warnings:         {total_warnings}")
    print(f"Errors:           {total_errors}")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="JSON to Semantic Chunking Pipeline (.jsonl)")
    parser.add_argument(
        "--input", "-i",
        type=str,
        default="json",
        help="Input folder containing JSON files (default: json)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="chunks",
        help="Output folder for generated JSONL files (default: chunks)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=700,
        help="Target chunk size in tokens (default: 700)"
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=100,
        help="Chunk overlap size in tokens (default: 100)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate JSON files and chunk structures without writing output files"
    )
    parser.add_argument(
        "--md-to-json",
        action="store_true",
        help="Run Stage 1 (Markdown to JSON) pipeline first"
    )

    args = parser.parse_args()

    if args.md_to_json:
        converter = BookConverter(input_dir="markdown", output_dir="json")
        converter.process_all()

    config = ChunkerConfig(
        input_dir=args.input,
        output_dir=args.output,
        chunk_size=args.chunk_size,
        chunk_overlap=args.overlap
    )

    run_chunker_pipeline(config, validate_only=args.validate)


if __name__ == "__main__":
    main()
