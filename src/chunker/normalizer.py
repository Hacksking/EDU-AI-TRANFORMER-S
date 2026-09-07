import re
from typing import Dict, Any, List
from .code_detector import CodeDetector

class SchemaNormalizer:
    """Normalizes document JSON structure, demoting fake code headings to code nodes."""

    @classmethod
    def is_fake_code_heading(cls, title: str) -> bool:
        """Determines if a section title is actually a code snippet mistaken for a heading."""
        t = title.strip()
        if not t:
            return False
            
        # Code statements ending with semicolon or containing C/C++ declarations/calls
        if re.search(r";\s*$", t):
            return True
        if re.search(r"^\s*(int|void|char|double|float|long|short|struct)\b.*[=;\[\)]", t):
            return True
        if re.search(r"//.*|/\*.*\*/", t):
            return True
        if re.search(r"^\s*\w+\s*\([^)]*\)\s*;", t):
            return True
            
        return False

    @classmethod
    def normalize_content_node(cls, node: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures a content node dictionary has standard type and attributes."""
        ntype = node.get("type", "paragraph")
        
        if ntype == "code":
            raw_code = node.get("code", "")
            hint_lang = node.get("language")
            detected = CodeDetector.detect_language(raw_code, hint_lang)
            return {
                "type": "code",
                "language": detected,
                "code": raw_code
            }
        elif ntype == "paragraph":
            text = node.get("text", "")
            # Check if paragraph contains unformatted code block
            if CodeDetector.is_code(text) and ("int " in text or "return " in text or "//" in text or ";" in text):
                detected = CodeDetector.detect_language(text)
                return {
                    "type": "code",
                    "language": detected,
                    "code": text
                }
            return {
                "type": "paragraph",
                "text": text
            }
        elif ntype == "table":
            return {
                "type": "table",
                "headers": node.get("headers", []),
                "rows": node.get("rows", [])
            }
        elif ntype == "list":
            return {
                "type": "list",
                "ordered": node.get("ordered", False),
                "items": node.get("items", [])
            }
        elif ntype in ["note", "warning", "quote"]:
            return {
                "type": ntype,
                "text": node.get("text", "")
            }
        elif ntype == "image":
            return {
                "type": "image",
                "alt": node.get("alt", ""),
                "src": node.get("src", "")
            }
        elif ntype == "link":
            return {
                "type": "link",
                "text": node.get("text", ""),
                "url": node.get("url", "")
            }
        else:
            return {
                "type": ntype if ntype else "raw",
                "text": node.get("text", str(node))
            }

    @classmethod
    def normalize_section(cls, sec: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively normalizes a section dict and resolves fake code headings."""
        sec_title = sec.get("title", "")
        normalized_content = []
        
        # Normalize existing content
        for item in sec.get("content", []):
            normalized_content.append(cls.normalize_content_node(item))
            
        normalized_subsections = []
        for subsec in sec.get("sections", []):
            sub_title = subsec.get("title", "")
            if cls.is_fake_code_heading(sub_title):
                # Demote fake code heading to code content node!
                detected_lang = CodeDetector.detect_language(sub_title)
                code_node = {
                    "type": "code",
                    "language": detected_lang,
                    "code": sub_title
                }
                normalized_content.append(code_node)
                
                # Transfer sub-content
                for sub_item in subsec.get("content", []):
                    normalized_content.append(cls.normalize_content_node(sub_item))
            else:
                normalized_subsections.append(cls.normalize_section(subsec))
                
        result = {
            "id": sec.get("id", ""),
            "title": sec_title,
            "level": sec.get("level", 2),
            "content": normalized_content
        }
        if normalized_subsections:
            result["sections"] = normalized_subsections
        if "line_start" in sec:
            result["line_start"] = sec["line_start"]
        if "line_end" in sec:
            result["line_end"] = sec["line_end"]
            
        return result

    @classmethod
    def normalize_book(cls, book_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes full book JSON structure."""
        meta = book_data.get("book", {})
        chapters = book_data.get("chapters", [])
        
        normalized_chapters = []
        for chap in chapters:
            chap_title = chap.get("title", "")
            chap_sections = []
            
            for sec in chap.get("sections", []):
                sec_title = sec.get("title", "")
                if cls.is_fake_code_heading(sec_title):
                    # Demote fake section title to code block inside preceding section or new section
                    detected_lang = CodeDetector.detect_language(sec_title)
                    code_node = {
                        "type": "code",
                        "language": detected_lang,
                        "code": sec_title
                    }
                    if chap_sections:
                        chap_sections[-1]["content"].append(code_node)
                        for item in sec.get("content", []):
                            chap_sections[-1]["content"].append(cls.normalize_content_node(item))
                    else:
                        norm_sec = cls.normalize_section(sec)
                        norm_sec["title"] = "Code Snippet"
                        chap_sections.append(norm_sec)
                else:
                    chap_sections.append(cls.normalize_section(sec))
                    
            norm_chap = {
                "id": chap.get("id", ""),
                "number": chap.get("number"),
                "title": chap_title,
                "sections": chap_sections,
                "source": chap.get("source", {})
            }
            normalized_chapters.append(norm_chap)
            
        return {
            "book": meta,
            "chapters": normalized_chapters
        }
