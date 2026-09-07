import json
from typing import Dict, Any, List, Set, Tuple

class JSONValidator:
    """Validates the output JSON structure for schema correctness, unique IDs, and content preservation."""

    @staticmethod
    def validate_dict(data: Dict[str, Any], initial_warnings: List[str] = None) -> Dict[str, Any]:
        warnings = list(initial_warnings) if initial_warnings else []
        seen_ids: Set[str] = set()

        stats = {
            "success": True,
            "chapters": 0,
            "sections": 0,
            "code_blocks": 0,
            "tables": 0,
            "images": 0,
            "links": 0,
            "warnings_count": 0,
            "warnings": warnings
        }

        # 1. Top-level keys check
        if "book" not in data or "chapters" not in data:
            warnings.append("Missing top-level 'book' or 'chapters' key.")
            stats["success"] = False
            return stats

        book_meta = data.get("book", {})
        required_meta = ["id", "title", "authors", "source_file", "language", "total_chapters"]
        for key in required_meta:
            if key not in book_meta:
                warnings.append(f"Missing required book metadata key: '{key}'")
                stats["success"] = False

        if book_meta.get("id"):
            seen_ids.add(book_meta["id"])

        chapters = data.get("chapters", [])
        stats["chapters"] = len(chapters)

        def count_content_nodes(nodes: List[Dict[str, Any]]):
            for n in nodes:
                t = n.get("type")
                if t == "code":
                    stats["code_blocks"] += 1
                elif t == "table":
                    stats["tables"] += 1
                elif t == "image":
                    stats["images"] += 1
                elif t == "link":
                    stats["links"] += 1
                elif t == "raw":
                    warnings.append(f"Raw block preserved: {n.get('text', '')[:40]}...")

        def validate_sections(sections: List[Dict[str, Any]]):
            for sec in sections:
                stats["sections"] += 1
                sec_id = sec.get("id")
                if sec_id:
                    if sec_id in seen_ids:
                        warnings.append(f"Duplicate section ID found: '{sec_id}'")
                    seen_ids.add(sec_id)
                else:
                    warnings.append("Section missing required 'id' field.")

                if "title" not in sec or "level" not in sec:
                    warnings.append(f"Section '{sec_id}' missing 'title' or 'level'.")

                count_content_nodes(sec.get("content", []))

                # Recursively validate subsections
                if "sections" in sec and isinstance(sec["sections"], list):
                    validate_sections(sec["sections"])

        # Validate chapters
        for idx, chap in enumerate(chapters, start=1):
            chap_id = chap.get("id")
            if chap_id:
                if chap_id in seen_ids:
                    warnings.append(f"Duplicate chapter ID found: '{chap_id}'")
                seen_ids.add(chap_id)
            else:
                warnings.append(f"Chapter at index {idx} missing 'id'.")

            if "title" not in chap or "sections" not in chap:
                warnings.append(f"Chapter '{chap_id}' missing 'title' or 'sections'.")

            validate_sections(chap.get("sections", []))

        stats["warnings_count"] = len(warnings)
        return stats

    @classmethod
    def validate_file(cls, json_filepath: str, initial_warnings: List[str] = None) -> Dict[str, Any]:
        """Loads a JSON file and runs validation."""
        try:
            with open(json_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.validate_dict(data, initial_warnings)
        except Exception as e:
            return {
                "success": False,
                "chapters": 0,
                "sections": 0,
                "code_blocks": 0,
                "tables": 0,
                "images": 0,
                "links": 0,
                "warnings_count": 1,
                "warnings": [f"Failed to read/parse JSON file: {str(e)}"]
            }
