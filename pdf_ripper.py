#!/usr/bin/env python3
"""
PDF Ripper - Extracts text from PDF files using OCR and saves to a single markdown file.
"""

import argparse
import sys
from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io


def extract_pages_to_markdown(
    pdf_path: str,
    output_file: str,
    pages_per_chunk: int = 10,
    dpi: int = 300
) -> None:
    """
    Extract text from a PDF file using OCR and save to a single markdown file.
    Processes in chunks for progress reporting.

    Args:
        pdf_path: Path to the input PDF file.
        output_file: Path to the output markdown file.
        pages_per_chunk: Number of pages to process per progress update.
        dpi: Resolution for rendering PDF pages (higher = better quality, slower).
    """
    pdf_path = Path(pdf_path)
    output_file = Path(output_file)

    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")
    print(f"Output file: {output_file}")
    print(f"Using OCR at {dpi} DPI")

    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {pdf_path.stem}\n\n")
        f.write(f"Extracted from: {pdf_path.name}\n\n")
        f.write(f"Total pages: {total_pages}\n\n")
        f.write("---\n\n")

        start_page = 0

        while start_page < total_pages:
            end_page = min(start_page + pages_per_chunk, total_pages)

            print(f"Processing pages {start_page + 1} to {end_page}...")

            for page_num in range(start_page, end_page):
                page = doc[page_num]

                pix = page.get_pixmap(matrix=matrix)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))

                text = pytesseract.image_to_string(img)

                f.write(f"## Page {page_num + 1}\n\n")
                f.write(text.strip())
                f.write("\n\n")

            start_page = end_page

    doc.close()

    print(f"\nComplete. Saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDF using OCR and save to a single markdown file."
    )
    parser.add_argument(
        "pdf_path",
        help="Path to the input PDF file"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output markdown file path (default: output/<pdf_name>.md)"
    )
    parser.add_argument(
        "-p", "--pages-per-chunk",
        type=int,
        default=10,
        help="Number of pages per progress update (default: 10)"
    )
    parser.add_argument(
        "-d", "--dpi",
        type=int,
        default=300,
        help="DPI for rendering pages (default: 300, higher = better quality but slower)"
    )

    args = parser.parse_args()

    if args.output is None:
        pdf_name = Path(args.pdf_path).stem
        output_file = f"output/{pdf_name}.md"
    else:
        output_file = args.output

    extract_pages_to_markdown(
        pdf_path=args.pdf_path,
        output_file=output_file,
        pages_per_chunk=args.pages_per_chunk,
        dpi=args.dpi
    )


if __name__ == "__main__":
    main()
