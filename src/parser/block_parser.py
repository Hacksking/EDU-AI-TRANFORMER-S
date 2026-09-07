import re
from typing import Dict, Any, List, Optional, Tuple
from ..models.content import (
    ParagraphNode, CodeNode, HeadingNode, ListNode,
    QuoteNode, TableNode, ImageNode, LinkNode,
    NoteNode, WarningNode, RawNode, ContentNode
)

def is_code_fence(line: str) -> Tuple[bool, Optional[str]]:
    """Checks if a line opens or closes a fenced code block."""
    match = re.match(r"^```\s*([\w+\-#]*)\s*$", line.strip())
    if match:
        lang = match.group(1).strip()
        return True, (lang if lang else None)
    return False, None

def is_table_row(line: str) -> bool:
    """Checks if a line looks like a Markdown table row."""
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 2

def is_table_delimiter(line: str) -> bool:
    """Checks if a line is a Markdown table header delimiter row (e.g. |---|---|)."""
    stripped = line.strip()
    if not is_table_row(line):
        return False
    cells = [c.strip() for c in stripped[1:-1].split("|")]
    return all(re.match(r"^:?-+:?$", c) for c in cells if c)

def parse_table(block_lines: List[str]) -> Optional[TableNode]:
    """Parses Markdown table lines into a TableNode."""
    try:
        rows_data = []
        for line in block_lines:
            stripped = line.strip()
            if stripped.startswith("|") and stripped.endswith("|"):
                cells = [c.strip() for c in stripped[1:-1].split("|")]
                rows_data.append(cells)
                
        if len(rows_data) < 2:
            return None
            
        headers = rows_data[0]
        data_rows = []
        
        # Skip delimiter row if present
        start_idx = 1
        if start_idx < len(rows_data) and all(re.match(r"^:?-+:?$", c) for c in rows_data[1] if c):
            start_idx = 2
            
        for row in rows_data[start_idx:]:
            data_rows.append(row)
            
        return TableNode(headers=headers, rows=data_rows)
    except Exception:
        return None

def parse_list(block_lines: List[str]) -> Optional[ListNode]:
    """Parses list lines into a ListNode."""
    items = []
    ordered = False
    
    first_line = block_lines[0].strip()
    if re.match(r"^\d+[\.\)]\s+", first_line):
        ordered = True
        
    current_item = []
    
    for line in block_lines:
        stripped = line.strip()
        is_new_item = False
        item_text = ""
        
        if ordered:
            m = re.match(r"^\d+[\.\)]\s+(.*)$", stripped)
            if m:
                is_new_item = True
                item_text = m.group(1)
        else:
            m = re.match(r"^[•\-\*\+]\s+(.*)$", stripped)
            if m:
                is_new_item = True
                item_text = m.group(1)
                
        if is_new_item:
            if current_item:
                items.append(" ".join(current_item))
            current_item = [item_text]
        else:
            if current_item:
                current_item.append(stripped)
            else:
                current_item = [stripped]
                
    if current_item:
        items.append(" ".join(current_item))
        
    if items:
        return ListNode(items=items, ordered=ordered)
    return None

def parse_block(block_text: str, warnings_list: Optional[List[str]] = None) -> ContentNode:
    """Parses a text block into a ContentNode."""
    lines = block_text.split("\n")
    stripped = block_text.strip()
    
    if not stripped:
        return ParagraphNode(text="")
        
    # 1. Code Block
    if lines[0].strip().startswith("```") and lines[-1].strip().startswith("```") and len(lines) >= 2:
        is_fence, lang = is_code_fence(lines[0])
        code_lines = lines[1:-1]
        code_content = "\n".join(code_lines)
        return CodeNode(code=code_content, language=lang)

    # 2. Image Block (standalone)
    img_match = re.match(r"^!\[(.*?)\]\((.*?)\)$", stripped)
    if img_match:
        return ImageNode(alt=img_match.group(1), src=img_match.group(2))

    # 3. Link Block (standalone)
    link_match = re.match(r"^\[(.*?)\]\((.*?)\)$", stripped)
    if link_match:
        return LinkNode(text=link_match.group(1), url=link_match.group(2))

    # 4. Table Block
    if is_table_row(lines[0]) and len(lines) >= 2:
        table_node = parse_table(lines)
        if table_node:
            return table_node
        else:
            if warnings_list is not None:
                warnings_list.append("Unable to parse table structure cleanly. Preserved as raw.")
            return RawNode(text=block_text)

    # 5. Callouts & Blockquotes
    if all(line.strip().startswith(">") for line in lines if line.strip()):
        quote_text_lines = []
        for line in lines:
            s = line.strip()
            if s.startswith(">"):
                quote_text_lines.append(s[1:].strip())
            else:
                quote_text_lines.append(s)
        full_quote = " ".join(quote_text_lines)
        
        # Check Note callout
        note_match = re.match(r"^\*\*(Note|NOTE):\*\*\s*(.*)$", full_quote, re.IGNORECASE)
        if note_match:
            return NoteNode(text=note_match.group(2))
        note_match2 = re.match(r"^(Note|NOTE):\s*(.*)$", full_quote, re.IGNORECASE)
        if note_match2:
            return NoteNode(text=note_match2.group(2))
            
        # Check Warning callout
        warn_match = re.match(r"^\*\*(Warning|WARNING|Caution|CAUTION):\*\*\s*(.*)$", full_quote, re.IGNORECASE)
        if warn_match:
            return WarningNode(text=warn_match.group(2))
        warn_match2 = re.match(r"^(Warning|WARNING|Caution|CAUTION):\s*(.*)$", full_quote, re.IGNORECASE)
        if warn_match2:
            return WarningNode(text=warn_match2.group(2))
            
        return QuoteNode(text=full_quote)

    # 6. List Block
    if (re.match(r"^[•\-\*\+]\s+", lines[0].strip()) or re.match(r"^\d+[\.\)]\s+", lines[0].strip())):
        list_node = parse_list(lines)
        if list_node:
            return list_node

    # 7. Heading (Inline block heading)
    heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
    if heading_match:
        level = len(heading_match.group(1))
        title = heading_match.group(2)
        return HeadingNode(text=title, level=level)

    # 8. Standard Paragraph
    return ParagraphNode(text=stripped)
