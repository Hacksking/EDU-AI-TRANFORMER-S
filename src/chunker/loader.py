import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

class JSONLoader:
    """Discovers and safely loads JSON book files."""

    def __init__(self, logs_dir: str = "logs"):
        self.logs_path = Path(logs_dir).resolve()
        self.logs_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("JSONLoader")
        
        handler = logging.FileHandler(self.logs_path / "pipeline.log", encoding="utf-8")
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def load_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
            return data
        except Exception as e:
            err_msg = f"ERROR: {filepath.name} - Reason: invalid JSON or read failure ({str(e)})"
            self.logger.error(err_msg)
            print(f"      ✗ {err_msg}")
            return None

    def discover_files(self, input_dir: Path) -> List[Path]:
        if not input_dir.exists():
            return []
        files = sorted(list(input_dir.glob("*.json")) + list(input_dir.glob("*.JSON")))
        return sorted(list(dict.fromkeys([f.resolve() for f in files])))
