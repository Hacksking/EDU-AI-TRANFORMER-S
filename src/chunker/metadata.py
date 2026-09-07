from typing import Dict, Any, Optional

class MetadataGenerator:
    """Generates deterministic chunk IDs, context metadata, and source traceability."""

    @staticmethod
    def generate_chunk_id(
        book_id: str,
        chap_num: Optional[int],
        sec_idx: int,
        chunk_idx: int
    ) -> str:
        """Generates a deterministic chunk ID."""
        c_str = f"ch{chap_num:02d}" if chap_num is not None else "ch00"
        s_str = f"sec{sec_idx:02d}"
        k_str = f"chunk{chunk_idx:03d}"
        return f"{book_id}-{c_str}-{s_str}-{k_str}"

    @staticmethod
    def build_context(
        book_title: Optional[str] = None,
        chapter_title: Optional[str] = None,
        section_title: Optional[str] = None,
        subsection_title: Optional[str] = None
    ) -> Dict[str, str]:
        """Builds context dictionary omitting None or empty fields."""
        ctx = {}
        if book_title:
            ctx["book_title"] = book_title
        if chapter_title:
            ctx["chapter_title"] = chapter_title
        if section_title:
            ctx["section_title"] = section_title
        if subsection_title:
            ctx["subsection_title"] = subsection_title
        return ctx

    @staticmethod
    def build_source(
        source_file: str,
        line_start: Optional[int] = None,
        line_end: Optional[int] = None,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None
    ) -> Dict[str, Any]:
        """Builds source traceability dictionary."""
        src = {"file": source_file}
        if line_start is not None:
            src["line_start"] = line_start
        if line_end is not None:
            src["line_end"] = line_end
        if page_start is not None:
            src["page_start"] = page_start
        if page_end is not None:
            src["page_end"] = page_end
        return src
