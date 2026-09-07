import sys
from typing import Dict, Any, List

class TerminalReporter:
    """Utility class to format and display conversion progress and validation metrics."""
    
    @staticmethod
    def print_start(input_dir: str, file_count: int):
        print(f"Scanning {input_dir}/...\n")
        print(f"Found {file_count} Markdown file(s).\n")

    @staticmethod
    def print_file_result(
        current_idx: int,
        total_files: int,
        filename: str,
        stats: Dict[str, Any],
        output_json_path: str
    ):
        print(f"[{current_idx}/{total_files}] {filename}")
        if stats.get("success", True):
            print("      [OK] Parsed")
        else:
            print("      [FAIL] Failed to Parse")
            
        print(f"      - Chapters: {stats.get('chapters', 0)}")
        print(f"      - Sections: {stats.get('sections', 0)}")
        print(f"      - Code blocks: {stats.get('code_blocks', 0)}")
        print(f"      - Tables: {stats.get('tables', 0)}")
        print(f"      - Warnings: {stats.get('warnings_count', 0)}")
        
        for w in stats.get("warnings", []):
            print(f"        WARNING: {w}")
            
        print(f"      -> {output_json_path}\n")

    @staticmethod
    def print_complete(total_files: int, total_chapters: int, total_sections: int, total_warnings: int):
        print("=" * 60)
        print("CONVERSION COMPLETE")
        print("=" * 60)
        print(f"Total Markdown Files: {total_files}")
        print(f"Total Chapters:       {total_chapters}")
        print(f"Total Sections:       {total_sections}")
        print(f"Total Warnings:       {total_warnings}")
        print("=" * 60)
