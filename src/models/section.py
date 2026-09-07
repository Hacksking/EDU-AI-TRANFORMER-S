from typing import List, Dict, Any, Optional
from .content import ContentNode

class Section:
    """Represents a section (heading block) within a chapter."""
    def __init__(
        self,
        section_id: str,
        title: str,
        level: int = 2,
        content: Optional[List[Any]] = None,
        sections: Optional[List['Section']] = None,
        line_start: Optional[int] = None,
        line_end: Optional[int] = None
    ):
        self.id = section_id
        self.title = title
        self.level = level
        self.content = content if content is not None else []
        self.sections = sections if sections is not None else []
        self.line_start = line_start
        self.line_end = line_end

    def to_dict(self) -> Dict[str, Any]:
        content_dicts = [
            item.to_dict() if hasattr(item, "to_dict") else item
            for item in self.content
        ]
        subsection_dicts = [s.to_dict() for s in self.sections]
        
        result = {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "content": content_dicts
        }
        if subsection_dicts:
            result["sections"] = subsection_dicts
            
        if self.line_start is not None:
            result["line_start"] = self.line_start
        if self.line_end is not None:
            result["line_end"] = self.line_end
            
        return result
