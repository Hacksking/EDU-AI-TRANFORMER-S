import os
import sys
import time
import re
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

import pymupdf

# Suppress internal PyMuPDF warning messages
try:
    pymupdf.set_messages(False)
except Exception:
    pass


def convert_block_to_md(block_text: str) -> str:
    """Converts a raw PyMuPDF text block into clean Markdown."""
    text = block_text.strip()
    if not text:
        return ""
        
    lines = text.split("\n")
    
    # 1. Heading heuristics (short text, no ending period, section numbers / titles)
    if len(lines) <= 2 and len(text) < 120 and not text.endswith("."):
        if re.match(r"^(Chapter|\d+(\.\d+)*)\b", text, re.IGNORECASE):
            return f"## {text}"
        elif text.isupper() or len(lines) == 1:
            return f"### {text}"

    # 2. Code block heuristics (indented lines or programming keywords)
    if any(line.startswith(("    ", "\t")) for line in lines) or any(
        kw in text for kw in ["def ", "class ", "#include", "import ", "public static", "function(", "const ", "let ", "var "]
    ):
        return f"```\n{text}\n```"

    # 3. List item heuristics
    if lines[0].lstrip().startswith(("•", "-", "*", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
        return "\n".join(lines)

    # 4. Regular paragraph: fix hyphenated line breaks and join lines cleanly
    paragraph = text.replace("-\n", "").replace("\n", " ")
    return paragraph


def convert_single_pdf(pdf_path_str: str, output_dir_str: str) -> dict:
    """Reads a single PDF file and writes its converted Markdown version to output_dir."""
    pdf_path = Path(pdf_path_str)
    output_dir = Path(output_dir_str)
    start_time = time.time()
    
    md_filename = pdf_path.stem + ".md"
    output_file = output_dir / md_filename
    
    try:
        doc = pymupdf.open(str(pdf_path))
        page_mds = []
        
        for idx in range(len(doc)):
            page = doc[idx]
            blocks = page.get_text("blocks")
            
            page_blocks = []
            for b in blocks:
                # b[6] == 0 indicates a text block in PyMuPDF
                if b[6] == 0:
                    formatted_block = convert_block_to_md(b[4])
                    if formatted_block:
                        page_blocks.append(formatted_block)
                        
            page_content = "\n\n".join(page_blocks)
            if page_content.strip():
                page_mds.append(f"<!-- Page {idx + 1} -->\n\n{page_content}")
                
        doc.close()
        
        full_markdown = f"# {pdf_path.stem}\n\n" + "\n\n---\n\n".join(page_mds)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_markdown)
            
        duration = time.time() - start_time
        size_kb = output_file.stat().st_size / 1024
        
        return {
            "file": pdf_path.name,
            "status": "SUCCESS",
            "output": str(output_file),
            "size_kb": round(size_kb, 2),
            "duration": round(duration, 2),
            "error": None
        }
    except Exception as e:
        duration = time.time() - start_time
        return {
            "file": pdf_path.name,
            "status": "FAILED",
            "output": str(output_file),
            "size_kb": 0,
            "duration": round(duration, 2),
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="PDF to Markdown Converter")
    parser.add_argument(
        "--input", "-i", type=str, default="PDFS", help="Path to input folder or single PDF file (default: PDFS)"
    )
    parser.add_argument(
        "--output", "-o", type=str, default="markdown", help="Path to output folder for Markdown files (default: markdown)"
    )
    parser.add_argument(
        "--workers", "-w", type=int, default=8, help="Number of parallel workers (default: 8)"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()
    
    if not input_path.exists():
        print(f"Error: Input path '{input_path}' does not exist.")
        sys.exit(1)
        
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if input_path.is_file():
        pdf_files = [input_path]
    else:
        all_files = list(input_path.glob("*.pdf")) + list(input_path.glob("*.PDF"))
        pdf_files = sorted(list(dict.fromkeys([p.resolve() for p in all_files])))
        
    if not pdf_files:
        print(f"No PDF files found in '{input_path}'.")
        sys.exit(0)
        
    print(f"Found {len(pdf_files)} PDF file(s) to process.")
    print(f"Output directory: '{output_dir}'.")
    print(f"Processing with {args.workers} worker(s)...\n")
    
    results = []
    start_total = time.time()
    
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_pdf = {
            executor.submit(convert_single_pdf, str(pdf), str(output_dir)): pdf
            for pdf in pdf_files
        }
        
        for future in tqdm(as_completed(future_to_pdf), total=len(pdf_files), desc="Converting PDFs"):
            res = future.result()
            results.append(res)
            if res["status"] == "SUCCESS":
                tqdm.write(f"[OK] [{res['file']}] -> {res['size_kb']} KB ({res['duration']}s)")
            else:
                tqdm.write(f"[FAIL] [{res['file']}] FAILED: {res['error']}")
                
    total_time = time.time() - start_total
    successful = [r for r in results if r["status"] == "SUCCESS"]
    failed = [r for r in results if r["status"] == "FAILED"]
    
    print("\n" + "=" * 65)
    print("CONVERSION SUMMARY")
    print("=" * 65)
    print(f"Total PDFs found:       {len(pdf_files)}")
    print(f"Successfully converted: {len(successful)}")
    print(f"Failed:                 {len(failed)}")
    print(f"Total time elapsed:     {round(total_time, 2)} seconds")
    print(f"Output directory:       {output_dir}")
    print("=" * 65)


if __name__ == "__main__":
    main()
