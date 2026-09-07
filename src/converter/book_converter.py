import json
from pathlib import Path
from typing import Dict, Any, List

from ..parser.md_parser import MarkdownParser
from ..validator.json_validator import JSONValidator
from ..utils.reporter import TerminalReporter

class BookConverter:
    """Orchestrates reading Markdown files, parsing them, validating JSON, and writing outputs."""
    
    def __init__(self, input_dir: str = "markdown", output_dir: str = "json"):
        self.input_dir = Path(input_dir).resolve()
        self.output_dir = Path(output_dir).resolve()

    def process_all(self) -> Dict[str, Any]:
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory '{self.input_dir}' does not exist.")
            
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        md_files = sorted(list(self.input_dir.glob("*.md")) + list(self.input_dir.glob("*.MD")))
        md_files = sorted(list(dict.fromkeys([f.resolve() for f in md_files])))
        
        total_files = len(md_files)
        TerminalReporter.print_start(str(self.input_dir), total_files)
        
        total_chapters = 0
        total_sections = 0
        total_warnings = 0
        file_results = []
        
        for idx, md_file in enumerate(md_files, start=1):
            json_filename = md_file.stem + ".json"
            output_json_path = self.output_dir / json_filename
            
            # 1. Parse Markdown
            parser = MarkdownParser(str(md_file))
            book_obj, parse_warnings = parser.parse()
            book_dict = book_obj.to_dict()
            
            # 2. Write JSON
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(book_dict, f, indent=2, ensure_ascii=False)
                
            # 3. Validate JSON file
            validation_stats = JSONValidator.validate_file(str(output_json_path), parse_warnings)
            
            # 4. Report single file result
            rel_output_path = f"json/{json_filename}"
            TerminalReporter.print_file_result(
                current_idx=idx,
                total_files=total_files,
                filename=md_file.name,
                stats=validation_stats,
                output_json_path=rel_output_path
            )
            
            total_chapters += validation_stats.get("chapters", 0)
            total_sections += validation_stats.get("sections", 0)
            total_warnings += validation_stats.get("warnings_count", 0)
            file_results.append(validation_stats)

        TerminalReporter.print_complete(total_files, total_chapters, total_sections, total_warnings)
        
        return {
            "total_files": total_files,
            "total_chapters": total_chapters,
            "total_sections": total_sections,
            "total_warnings": total_warnings,
            "files": file_results
        }
