from typing import List, Dict, Any, Optional

class ContentNode:
    """Base class for all content node elements."""
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError

class ParagraphNode(ContentNode):
    def __init__(self, text: str):
        self.text = text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "paragraph",
            "text": self.text
        }

class CodeNode(ContentNode):
    def __init__(self, code: str, language: Optional[str] = None):
        self.code = code
        self.language = language

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "code",
            "language": self.language,
            "code": self.code
        }

class HeadingNode(ContentNode):
    def __init__(self, text: str, level: int):
        self.text = text
        self.level = level

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "heading",
            "level": self.level,
            "text": self.text
        }

class ListNode(ContentNode):
    def __init__(self, items: List[Any], ordered: bool = False):
        self.items = items
        self.ordered = ordered

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "list",
            "ordered": self.ordered,
            "items": self.items
        }

class QuoteNode(ContentNode):
    def __init__(self, text: str):
        self.text = text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "quote",
            "text": self.text
        }

class TableNode(ContentNode):
    def __init__(self, headers: List[str], rows: List[List[str]]):
        self.headers = headers
        self.rows = rows

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "table",
            "headers": self.headers,
            "rows": self.rows
        }

class ImageNode(ContentNode):
    def __init__(self, alt: str, src: str):
        self.alt = alt
        self.src = src

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "image",
            "alt": self.alt,
            "src": self.src
        }

class LinkNode(ContentNode):
    def __init__(self, text: str, url: str):
        self.text = text
        self.url = url

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "link",
            "text": self.text,
            "url": self.url
        }

class NoteNode(ContentNode):
    def __init__(self, text: str):
        self.text = text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "note",
            "text": self.text
        }

class WarningNode(ContentNode):
    def __init__(self, text: str):
        self.text = text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "warning",
            "text": self.text
        }

class RawNode(ContentNode):
    def __init__(self, text: str):
        self.text = text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "raw",
            "text": self.text
        }
