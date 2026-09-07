import json
from pathlib import Path
from typing import List, Dict, Any

class JSONLWriter:
    """Writes chunk dictionaries to JSON Lines (.jsonl) files."""

    @staticmethod
    def write_jsonl(chunks: List[Dict[str, Any]], output_filepath: Path):
        output_filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(output_filepath, "w", encoding="utf-8") as f:
            for chunk in chunks:
                line = json.dumps(chunk, ensure_ascii=False)
                f.write(line + "\n")
