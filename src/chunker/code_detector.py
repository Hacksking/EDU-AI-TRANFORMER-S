import re
from typing import Optional, Tuple

class CodeDetector:
    """Detects programming code and identifies language types."""

    # Language signature patterns
    PATTERNS = {
        "python": [
            r"\bdef\s+\w+\s*\(", r"\bclass\s+\w+\s*\(", r"\bimport\s+\w+",
            r"\bfrom\s+\w+\s+import\b", r"\belif\s+.*:", r"\bprint\s*\(",
            r"\bself\.\w+", r"__init__"
        ],
        "cpp": [
            r"#include\s*<[w\.\/]+>", r"#include\s*\".*\"", r"std::\w+",
            r"cout\s*<<", r"cin\s*>>", r"template\s*<", r"using\s+namespace\s+std;",
            r"\bvector<", r"\bstring\b"
        ],
        "c": [
            r"#include\s*<stdio\.h>", r"#include\s*<stdlib\.h>", r"\bprintf\s*\(",
            r"\bscanf\s*\(", r"\bmalloc\s*\(", r"\bfree\s*\(", r"\bstruct\s+\w+",
            r"int\s+main\s*\(", r"\bint\s+\w+\s*\[\s*\]", r"\bint\s+\w+\s*=\s*sum\("
        ],
        "java": [
            r"public\s+class\s+\w+", r"public\s+static\s+void\s+main",
            r"System\.out\.println", r"import\s+java\.", r"private\s+\w+\s+\w+;"
        ],
        "javascript": [
            r"\bconst\s+\w+\s*=", r"\blet\s+\w+\s*=", r"\bvar\s+\w+\s*=",
            r"console\.log\s*\(", r"function\s*\w*\s*\(", r"=>\s*\{",
            r"document\.getElementById"
        ],
        "typescript": [
            r"interface\s+\w+\s*\{", r"type\s+\w+\s*=", r":\s*(string|number|boolean|any)\b",
            r"export\s+default\b"
        ],
        "csharp": [
            r"using\s+System;", r"namespace\s+\w+", r"Console\.WriteLine",
            r"public\s+class\s+\w+"
        ],
        "go": [
            r"package\s+main", r"import\s+\(\s*\"fmt\"", r"func\s+main\s*\(",
            r"fmt\.Println", r"\w+\s*:=\s*"
        ],
        "rust": [
            r"\bfn\s+\w+\s*\(", r"\blet\s+mut\s+", r"\bimpl\s+\w+",
            r"println!\s*\(", r"match\s+\w+\s*\{"
        ],
        "sql": [
            r"\bSELECT\b.*\bFROM\b", r"\bINSERT\s+INTO\b", r"\bUPDATE\b.*\bSET\b",
            r"\bCREATE\s+TABLE\b", r"\bWHERE\b.*\b="
        ],
        "bash": [
            r"^#!/bin/(bash|sh)", r"\bsudo\s+", r"\bchmod\s+", r"\bchown\s+",
            r"echo\s+\".*\"", r"grep\s+-"
        ]
    }

    @classmethod
    def is_code(cls, text: str) -> bool:
        """Determines if a block of text represents programming code."""
        text_str = text.strip()
        if not text_str:
            return False
            
        lines = text_str.split("\n")
        
        # 1. Multi-line code fence markers
        if lines[0].startswith("```") or text_str.startswith("// ") or text_str.startswith("/*"):
            return True
            
        # 2. Programming syntax indicators
        code_score = 0
        if re.search(r"[{};]\s*$", text_str, re.MULTILINE):
            code_score += 2
        if re.search(r"\b(int|void|char|double|float|bool|long|short)\s+\w+\s*[\(=\[]", text_str):
            code_score += 2
        if re.search(r"//.*|/\*[\s\S]*?\*/", text_str):
            code_score += 2
        if re.search(r"(\w+)\((.*?)\)", text_str) and (";" in text_str or "{" in text_str):
            code_score += 1

        for lang, patterns in cls.PATTERNS.items():
            for pat in patterns:
                if re.search(pat, text_str, re.IGNORECASE):
                    code_score += 2

        return code_score >= 2

    @classmethod
    def detect_language(cls, text: str, hinted_lang: Optional[str] = None) -> Optional[str]:
        """Detects language name or returns None if uncertain."""
        if hinted_lang and hinted_lang.strip():
            hint = hinted_lang.strip().lower()
            if hint in ["cpp", "c++"]:
                return "cpp"
            elif hint in ["c"]:
                return "c"
            elif hint in ["py", "python"]:
                return "python"
            elif hint in ["js", "javascript"]:
                return "javascript"
            elif hint in ["ts", "typescript"]:
                return "typescript"
            elif hint in ["java"]:
                return "java"
            elif hint in ["cs", "csharp", "c#"]:
                return "csharp"
            elif hint in ["go", "golang"]:
                return "go"
            elif hint in ["rs", "rust"]:
                return "rust"
            elif hint in ["sql"]:
                return "sql"
            elif hint in ["sh", "bash", "shell"]:
                return "bash"

        text_str = text.strip()
        scores = {}
        for lang, patterns in cls.PATTERNS.items():
            score = sum(1 for pat in patterns if re.search(pat, text_str, re.IGNORECASE))
            if score > 0:
                scores[lang] = score

        if scores:
            best_lang = max(scores, key=scores.get)
            if scores[best_lang] >= 1:
                return best_lang

        return None
