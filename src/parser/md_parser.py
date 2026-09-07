import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from ..models.content import ContentNode, RawNode
from ..models.section import Section
from ..models.chapter import Chapter
from ..models.book import BookMetadata, Book
from ..utils.slug import slugify, IdGenerator
from .block_parser import parse_block, is_code_fence, is_table_row

class MarkdownParser:
    """Parses a Markdown document into a structured Book instance."""
    
    def __init__(self, filepath: str):
        self.path = Path(filepath)
        self.filename = self.path.name
        self.book_id = slugify(self.path.stem)
        self.id_gen = IdGenerator(self.book_id)
        self.warnings: List[str] = []

    def _is_chapter_heading(self, line: str, level: int) -> Tuple[bool, Optional[int], str]:
        """Determines if a heading line represents a Chapter boundary."""
        text = line.lstrip("#").strip()
        
        # 1. Matches "Chapter 1", "Chapter 1: Title", "CHAPTER ONE", etc.
        m_chap = re.match(r"^chapter\s+(\d+|[ivxcldm]+)\s*[:\.-]?\s*(.*)$", text, re.IGNORECASE)
        if m_chap:
            num_str = m_chap.group(1)
            try:
                num = int(num_str)
            except ValueError:
                num = None
            title = m_chap.group(2).strip() or text
            return True, num, title
            
        # 2. Matches "1. Introduction", "1 Introduction" at Level 1 or 2
        m_num = re.match(r"^(\d+)[\.\s]+\s*(.+)$", text)
        if m_num and level <= 2:
            num = int(m_num.group(1))
            title = m_num.group(2).strip()
            return True, num, title
            
        # 3. Level 1 heading `# ...`
        if level == 1:
            return True, None, text
            
        return False, None, text

    def parse(self) -> Tuple[Book, List[str]]:
        with open(self.path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        if total_lines == 0:
            metadata = BookMetadata(
                book_id=self.book_id,
                title=self.path.stem,
                source_file=self.filename
            )
            return Book(metadata=metadata, chapters=[]), self.warnings

        # Extract book title from first H1 if present
        book_title = self.path.stem.replace("-", " ").replace("_", " ").title()
        for line in lines[:20]:
            if line.startswith("# "):
                title_cand = line[2:].strip()
                if title_cand:
                    book_title = title_cand
                    break

        chapters: List[Chapter] = []
        
        # Current active state
        current_chapter: Optional[Chapter] = None
        current_section_stack: List[Section] = []  # Stack for section hierarchy
        current_block_lines: List[str] = []
        block_line_start = 1

        in_code_block = False
        code_fence_lang = None

        def add_content_to_active(content_node: ContentNode):
            if current_section_stack:
                current_section_stack[-1].content.append(content_node)
            elif current_chapter:
                # Top-level content directly under chapter
                if not current_chapter.sections:
                    # Create an default section if none exists
                    sec_id = self.id_gen.generate_section_id(current_chapter.id, "Overview", 2)
                    sec = Section(
                        section_id=sec_id,
                        title="Overview",
                        level=2,
                        line_start=content_node if isinstance(content_node, int) else None
                    )
                    current_chapter.sections.append(sec)
                    current_section_stack.append(sec)
                current_chapter.sections[0].content.append(content_node)

        def flush_current_block(end_line_idx: int):
            nonlocal current_block_lines, block_line_start
            if not current_block_lines:
                return
                
            raw_block = "".join(current_block_lines)
            if raw_block.strip():
                node = parse_block(raw_block, warnings_list=self.warnings)
                add_content_to_active(node)
                
            current_block_lines = []

        def start_new_chapter(chap_num: Optional[int], title: str, line_no: int):
            nonlocal current_chapter, current_section_stack
            if current_chapter:
                current_chapter.line_end = line_no - 1
                
            chap_id = self.id_gen.generate_chapter_id(number=chap_num, title=title)
            current_chapter = Chapter(
                chapter_id=chap_id,
                title=title,
                number=chap_num if chap_num is not None else (len(chapters) + 1),
                source_file=self.filename,
                line_start=line_no
            )
            chapters.append(current_chapter)
            current_section_stack = []

        def add_section_header(title: str, level: int, line_no: int):
            nonlocal current_chapter, current_section_stack
            if not current_chapter:
                start_new_chapter(1, "Introduction", line_no)

            sec_id = self.id_gen.generate_section_id(current_chapter.id, title, level)
            new_sec = Section(
                section_id=sec_id,
                title=title,
                level=level,
                line_start=line_no
            )

            # Reconstruct hierarchy stack
            while current_section_stack and current_section_stack[-1].level >= level:
                popped = current_section_stack.pop()
                popped.line_end = line_no - 1

            if current_section_stack:
                # Add as subsection of parent
                current_section_stack[-1].sections.append(new_sec)
            else:
                # Top-level section under chapter
                current_chapter.sections.append(new_sec)

            current_section_stack.append(new_sec)

        # Parse document line by line
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Handle code block fence tracking
            if stripped.startswith("```"):
                if not in_code_block:
                    flush_current_block(idx - 1)
                    in_code_block = True
                    block_line_start = idx
                    current_block_lines.append(line)
                    continue
                else:
                    current_block_lines.append(line)
                    in_code_block = False
                    flush_current_block(idx)
                    continue

            if in_code_block:
                current_block_lines.append(line)
                continue

            # Heading Detection
            heading_m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if heading_m:
                flush_current_block(idx - 1)
                level = len(heading_m.group(1))
                h_text = heading_m.group(2).strip()

                if level == 1 and not chapters:
                    if "chapter" not in h_text.lower() and not re.match(r"^\d+[\.\s]", h_text):
                        book_title = h_text
                        has_explicit_chapters = any(
                            re.search(r"^#{1,2}\s+(chapter|\d+[\.\s])", l, re.IGNORECASE)
                            for l in lines[idx:]
                        )
                        if has_explicit_chapters:
                            block_line_start = idx + 1
                            continue

                is_chap, chap_num, chap_title = self._is_chapter_heading(line, level)
                if is_chap and (not chapters or level == 1 or "chapter" in h_text.lower()):
                    start_new_chapter(chap_num, chap_title, idx)
                else:
                    add_section_header(h_text, level, idx)
                block_line_start = idx + 1
                continue

            # Blank line boundaries
            if not stripped:
                flush_current_block(idx)
                block_line_start = idx + 1
                continue

            # Accumulate normal line
            if not current_block_lines:
                block_line_start = idx
            current_block_lines.append(line)

        # Flush final block
        flush_current_block(total_lines)
        if current_chapter and current_chapter.line_end is None:
            current_chapter.line_end = total_lines

        # Close out section end lines
        for sec in current_section_stack:
            if sec.line_end is None:
                sec.line_end = total_lines

        # Ensure at least one chapter exists
        if not chapters:
            start_new_chapter(1, "Overview", 1)
            current_chapter.line_end = total_lines

        metadata = BookMetadata(
            book_id=self.book_id,
            title=book_title,
            source_file=self.filename,
            total_chapters=len(chapters)
        )

        return Book(metadata=metadata, chapters=chapters), self.warnings
