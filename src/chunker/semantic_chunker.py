from typing import List, Dict, Any, Optional
from ..config import ChunkerConfig
from .structure import StructuralBlock
from .metadata import MetadataGenerator
from .code_detector import CodeDetector

def estimate_tokens(text: str) -> int:
    """Estimates token count for text using word count heuristic."""
    words = text.strip().split()
    return int(len(words) * 1.3) + 1

class SemanticChunker:
    """Core semantic chunker implementing structure-first token packing and overlap."""

    def __init__(self, config: Optional[ChunkerConfig] = None):
        self.config = config or ChunkerConfig()

    def _format_block_content(self, node: Dict[str, Any]) -> str:
        ntype = node.get("type", "paragraph")
        if ntype == "code":
            return node.get("code", "")
        elif ntype == "paragraph":
            return node.get("text", "")
        elif ntype == "list":
            items = node.get("items", [])
            prefix = "1. " if node.get("ordered") else "- "
            return "\n".join(f"{prefix}{item}" for item in items)
        elif ntype == "table":
            headers = node.get("headers", [])
            rows = node.get("rows", [])
            header_str = " | ".join(headers)
            delim_str = " | ".join(["---"] * len(headers))
            row_strs = [" | ".join(r) for r in rows]
            return f"| {header_str} |\n| {delim_str} |\n" + "\n".join(f"| {r} |" for r in row_strs)
        elif ntype in ["note", "warning", "quote"]:
            return f"[{ntype.upper()}] {node.get('text', '')}"
        else:
            return node.get("text", str(node))

    def create_chunk(
        self,
        content_str: str,
        content_type: str,
        language: Optional[str],
        primary_block: StructuralBlock,
        sec_idx: int,
        chunk_idx: int,
        line_start: Optional[int] = None,
        line_end: Optional[int] = None
    ) -> Dict[str, Any]:

        chunk_id = MetadataGenerator.generate_chunk_id(
            book_id=primary_block.book_id,
            chap_num=primary_block.chap_num,
            sec_idx=sec_idx,
            chunk_idx=chunk_idx
        )

        context = MetadataGenerator.build_context(
            book_title=primary_block.book_title,
            chapter_title=primary_block.chap_title,
            section_title=primary_block.sec_title,
            subsection_title=primary_block.subsec_title
        )

        source = MetadataGenerator.build_source(
            source_file=primary_block.source_file,
            line_start=line_start if line_start is not None else primary_block.line_start,
            line_end=line_end if line_end is not None else primary_block.line_end
        )

        return {
            "chunk_id": chunk_id,
            "book_id": primary_block.book_id,
            "chapter": {
                "number": primary_block.chap_num,
                "title": primary_block.chap_title
            },
            "section": {
                "title": primary_block.sec_title
            },
            "content_type": content_type,
            "language": language,
            "content": content_str,
            "context": context,
            "source": source
        }

    def chunk_blocks(self, blocks: List[StructuralBlock]) -> List[Dict[str, Any]]:
        if not blocks:
            return []

        # Group blocks by section key (chap_num, sec_title)
        section_groups: Dict[tuple, List[StructuralBlock]] = {}
        for b in blocks:
            key = (b.chap_num, b.sec_title)
            if key not in section_groups:
                section_groups[key] = []
            section_groups[key].append(b)

        chunks: List[Dict[str, Any]] = []

        for sec_idx, (sec_key, sec_blocks) in enumerate(section_groups.items(), start=1):
            chunk_counter = 1
            
            i = 0
            while i < len(sec_blocks):
                current_block = sec_blocks[i]
                node = current_block.node
                ntype = node.get("type", "paragraph")

                # Standalone Code Block
                if ntype == "code":
                    code_str = node.get("code", "").strip()
                    if code_str:
                        lang = node.get("language") or CodeDetector.detect_language(code_str)
                        chunk = self.create_chunk(
                            content_str=code_str,
                            content_type="code",
                            language=lang,
                            primary_block=current_block,
                            sec_idx=sec_idx,
                            chunk_idx=chunk_counter
                        )
                        chunks.append(chunk)
                        chunk_counter += 1
                    i += 1
                    continue

                # Standalone Table Block
                if ntype == "table":
                    table_str = self._format_block_content(node).strip()
                    if table_str:
                        chunk = self.create_chunk(
                            content_str=table_str,
                            content_type="table",
                            language=None,
                            primary_block=current_block,
                            sec_idx=sec_idx,
                            chunk_idx=chunk_counter
                        )
                        chunks.append(chunk)
                        chunk_counter += 1
                    i += 1
                    continue

                # Pack sequential text blocks
                pack_blocks = []
                current_tokens = 0
                has_code = False
                has_text = False

                j = i
                while j < len(sec_blocks):
                    b_next = sec_blocks[j]
                    b_type = b_next.node.get("type", "paragraph")

                    # Stop packing if we hit a large code block or table
                    if b_type in ["code", "table"] and pack_blocks:
                        break

                    block_text = self._format_block_content(b_next.node).strip()
                    if not block_text:
                        j += 1
                        continue

                    block_tokens = estimate_tokens(block_text)

                    if current_tokens + block_tokens > self.config.max_chunk_size and pack_blocks:
                        break

                    pack_blocks.append(b_next)
                    current_tokens += block_tokens
                    if b_type == "code":
                        has_code = True
                    else:
                        has_text = True

                    if current_tokens >= self.config.chunk_size:
                        j += 1
                        break

                    j += 1

                if pack_blocks:
                    combined_text = "\n\n".join(
                        self._format_block_content(b.node).strip() for b in pack_blocks
                    ).strip()

                    if combined_text:
                        if has_code and has_text:
                            c_type = "mixed"
                        elif has_code:
                            c_type = "code"
                        elif pack_blocks[0].node.get("type") in ["note", "warning", "quote"]:
                            c_type = pack_blocks[0].node.get("type")
                        elif pack_blocks[0].node.get("type") == "list":
                            c_type = "list"
                        else:
                            c_type = "text"

                        lang = None
                        if has_code:
                            lang = CodeDetector.detect_language(combined_text)

                        chunk = self.create_chunk(
                            content_str=combined_text,
                            content_type=c_type,
                            language=lang,
                            primary_block=pack_blocks[0],
                            sec_idx=sec_idx,
                            chunk_idx=chunk_counter,
                            line_start=pack_blocks[0].line_start,
                            line_end=pack_blocks[-1].line_end
                        )
                        chunks.append(chunk)
                        chunk_counter += 1

                i = max(j, i + 1)

        return chunks
