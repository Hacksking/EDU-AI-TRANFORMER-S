from typing import List, Dict, Any, Optional
from .section import Section

class Chapter:
    """Represents a chapter within a book."""
    def __init__(
        self,
        chapter_id: str,
        title: str,
        number: Optional[int] = None,
        sections: Optional[List[Section]] = None,
        source_file: Optional[str] = None,
        line_start: Optional[int] = None,
        line_end: Optional[int] = None
    ):
        self.id = chapter_id
        self.title = title
        self.number = number
        self.sections = sections if sections is not None else []
        self.source_file = source_file
        self.line_start = line_start
        self.line_end = line_end

    def to_dict(self) -> Dict[str, Any]:
        section_dicts = [s.to_dict() for s in self.sections]
        
        result = {
            "id": self.id,
            "number": self.number,
            "title": self.title,
            "sections": section_dicts
        }
        
        # Source traceability dictionary
        source_info: Dict[str, Any] = {}
        if self.source_file:
            source_info["file"] = self.source_file
        if self.number is not None:
            source_info["chapter"] = self.number
        source_info["heading"] = self.title
        if self.line_start is not None:
            source_info["line_start"] = self.line_start
        if self.line_end is not None:
            source_info["line_end"] = self.line_end
            
        result["source"] = source_info
        return result
