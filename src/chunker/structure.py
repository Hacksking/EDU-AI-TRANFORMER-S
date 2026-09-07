from typing import Dict, Any, List, Optional

class StructuralBlock:
    """Represents an atomic structural unit of content with document context."""
    
    def __init__(
        self,
        node: Dict[str, Any],
        book_id: str,
        book_title: str,
        chap_num: Optional[int],
        chap_title: str,
        sec_title: str,
        subsec_title: Optional[str] = None,
        source_file: str = "",
        line_start: Optional[int] = None,
        line_end: Optional[int] = None
    ):
        self.node = node
        self.book_id = book_id
        self.book_title = book_title
        self.chap_num = chap_num
        self.chap_title = chap_title
        self.sec_title = sec_title
        self.subsec_title = subsec_title
        self.source_file = source_file
        self.line_start = line_start
        self.line_end = line_end


class DocumentTraverser:
    """Traverses normalized book structure into a list of StructuralBlocks."""

    @classmethod
    def traverse_section(
        cls,
        sec: Dict[str, Any],
        book_id: str,
        book_title: str,
        chap_num: Optional[int],
        chap_title: str,
        parent_sec_title: str,
        source_file: str,
        blocks_out: List[StructuralBlock]
    ):
        sec_title = sec.get("title", parent_sec_title)
        line_start = sec.get("line_start")
        line_end = sec.get("line_end")

        for node in sec.get("content", []):
            b = StructuralBlock(
                node=node,
                book_id=book_id,
                book_title=book_title,
                chap_num=chap_num,
                chap_title=chap_title,
                sec_title=parent_sec_title if parent_sec_title != sec_title else sec_title,
                subsec_title=sec_title if parent_sec_title != sec_title else None,
                source_file=source_file,
                line_start=line_start,
                line_end=line_end
            )
            blocks_out.append(b)

        for subsec in sec.get("sections", []):
            cls.traverse_section(
                sec=subsec,
                book_id=book_id,
                book_title=book_title,
                chap_num=chap_num,
                chap_title=chap_title,
                parent_sec_title=sec_title,
                source_file=source_file,
                blocks_out=blocks_out
            )

    @classmethod
    def extract_blocks(cls, book_data: Dict[str, Any]) -> List[StructuralBlock]:
        meta = book_data.get("book", {})
        book_id = meta.get("id", "book")
        book_title = meta.get("title", "Book")
        source_file = meta.get("source_file", "book.json")

        blocks: List[StructuralBlock] = []

        for chap in book_data.get("chapters", []):
            chap_num = chap.get("number")
            chap_title = chap.get("title", "Chapter")

            for sec in chap.get("sections", []):
                cls.traverse_section(
                    sec=sec,
                    book_id=book_id,
                    book_title=book_title,
                    chap_num=chap_num,
                    chap_title=chap_title,
                    parent_sec_title=sec.get("title", "Section"),
                    source_file=source_file,
                    blocks_out=blocks
                )

        return blocks
