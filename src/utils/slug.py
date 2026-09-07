import re
from typing import Dict, Set

def slugify(text: str) -> str:
    """Converts a string into a deterministic URL/JSON safe slug."""
    text = text.lower().strip()
    # Replace non-alphanumeric chars with hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "untitled"

class IdGenerator:
    """Deterministic ID generator for books, chapters, and sections."""
    def __init__(self, book_slug: str):
        self.book_slug = book_slug
        self.used_ids: Set[str] = set()
        self.chapter_count = 0
        self.section_counts: Dict[str, int] = {}

    def generate_chapter_id(self, number: int = None, title: str = "") -> str:
        self.chapter_count += 1
        num = number if number is not None else self.chapter_count
        base_id = f"chapter-{num:02d}"
        
        final_id = base_id
        suffix_counter = 1
        while final_id in self.used_ids:
            suffix_counter += 1
            final_id = f"{base_id}-{suffix_counter}"
            
        self.used_ids.add(final_id)
        return final_id

    def generate_section_id(self, parent_id: str, title: str = "", level: int = 2) -> str:
        count = self.section_counts.get(parent_id, 0) + 1
        self.section_counts[parent_id] = count
        
        title_slug = slugify(title)
        if title_slug and len(title_slug) <= 30:
            base_id = f"{parent_id}-section-{count:02d}-{title_slug}"
        else:
            base_id = f"{parent_id}-section-{count:02d}"
            
        final_id = base_id
        suffix_counter = 1
        while final_id in self.used_ids:
            suffix_counter += 1
            final_id = f"{base_id}-{suffix_counter}"
            
        self.used_ids.add(final_id)
        return final_id
