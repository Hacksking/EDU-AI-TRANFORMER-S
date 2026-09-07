from typing import List, Dict, Any, Set

class ChunkerValidator:
    """Validates generated chunks for schema correctness, ID uniqueness, and content integrity."""

    @staticmethod
    def validate_chunks(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        seen_ids: Set[str] = set()
        warnings = []
        errors = []

        stats = {
            "total_chunks": len(chunks),
            "text": 0,
            "code": 0,
            "mixed": 0,
            "table": 0,
            "other": 0,
            "warnings_count": 0,
            "errors_count": 0,
            "warnings": warnings,
            "errors": errors
        }

        for idx, chunk in enumerate(chunks, start=1):
            cid = chunk.get("chunk_id")
            if not cid:
                errors.append(f"Chunk at index {idx} missing 'chunk_id'.")
            elif cid in seen_ids:
                errors.append(f"Duplicate chunk_id found: '{cid}'")
            else:
                seen_ids.add(cid)

            content = chunk.get("content", "")
            if not content or not content.strip():
                warnings.append(f"Chunk '{cid}' has empty content.")

            ctype = chunk.get("content_type", "text")
            if ctype == "text":
                stats["text"] += 1
            elif ctype == "code":
                stats["code"] += 1
            elif ctype == "mixed":
                stats["mixed"] += 1
            elif ctype == "table":
                stats["table"] += 1
            else:
                stats["other"] += 1

            if "source" not in chunk or "file" not in chunk.get("source", {}):
                warnings.append(f"Chunk '{cid}' missing source file metadata.")

        stats["warnings_count"] = len(warnings)
        stats["errors_count"] = len(errors)
        return stats
