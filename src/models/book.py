from typing import List, Dict, Any, Optional
from .chapter import Chapter

class BookMetadata:
    """Represents metadata for a book."""
    def __init__(
        self,
        book_id: str,
        title: str,
        source_file: str,
        authors: Optional[List[str]] = None,
        description: Optional[str] = None,
        language: str = "en",
        total_chapters: int = 0
    ):
        self.id = book_id
        self.title = title
        self.source_file = source_file
        self.authors = authors if authors is not None else []
        self.description = description
        self.language = language
        self.total_chapters = total_chapters

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "description": self.description,
            "source_file": self.source_file,
            "language": self.language,
            "total_chapters": self.total_chapters
        }

class Book:
    """Represents a complete book with metadata and chapters."""
    def __init__(self, metadata: BookMetadata, chapters: Optional[List[Chapter]] = None):
        self.metadata = metadata
        self.chapters = chapters if chapters is not None else []

    def to_dict(self) -> Dict[str, Any]:
        self.metadata.total_chapters = len(self.chapters)
        return {
            "book": self.metadata.to_dict(),
            "chapters": [c.to_dict() for c in self.chapters]
        }
