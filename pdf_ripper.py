#!/usr/bin/env python3
"""
PDF Ripper - Extracts text from PDF files using OCR and saves to a single markdown file.
Supports both single file processing and batch processing of all PDFs in a directory.
"""

import argparse
import sys
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io


DEFAULT_BOOKS_DIR = "books"
DEFAULT_OUTPUT_DIR = "output"


def get_pdf_files(directory: str) -> List[Path]:
    """
    Get all PDF files in a directory, sorted alphabetically.

    Args:
        directory: Path to the directory to scan.

    Returns:
        List of Path objects for each PDF file found.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Error: Directory not found: {dir_path}")
        sys.exit(1)

    pdf_files = sorted(dir_path.glob("*.pdf"), key=lambda p: p.name.lower())
    return pdf_files


def process_batch(
    books_dir: str,
    output_dir: str,
    pages_per_chunk: int = 10,
    dpi: int = 300,
    skip_existing: bool = True
) -> None:
    """
    Process all PDF files in the books directory.

    Args:
        books_dir: Path to directory containing PDF files.
        output_dir: Path to directory for output markdown files.
        pages_per_chunk: Number of pages to process per progress update.
        dpi: Resolution for rendering PDF pages.
        skip_existing: If True, skip PDFs that already have output files.
    """
    pdf_files = get_pdf_files(books_dir)

    if not pdf_files:
        print(f"No PDF files found in: {books_dir}")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    total_books = len(pdf_files)
    print(f"Found {total_books} PDF file(s) in {books_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 60)

    processed = 0
    skipped = 0
    failed = 0

    for index, pdf_file in enumerate(pdf_files, start=1):
        output_file = output_path / f"{pdf_file.stem}.md"

        print(f"\n[{index}/{total_books}] {pdf_file.name}")

        if skip_existing and output_file.exists():
            print(f"  Skipping: output file already exists")
            skipped += 1
            continue

        try:
            extract_pages_to_markdown(
                pdf_path=str(pdf_file),
                output_file=str(output_file),
                pages_per_chunk=pages_per_chunk,
                dpi=dpi
            )
            processed += 1
        except Exception as e:
            print(f"  Error processing {pdf_file.name}: {e}")
            failed += 1
            continue

    print("\n" + "=" * 60)
    print("Batch processing complete")
    print(f"  Processed: {processed}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")
    print(f"  Total:     {total_books}")


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
        description="Extract text from PDF using OCR and save to a single markdown file. "
                    "Supports single file or batch processing of all PDFs in a directory."
    )
    parser.add_argument(
        "pdf_path",
        nargs="?",
        default=None,
        help="Path to the input PDF file (required unless using --batch)"
    )
    parser.add_argument(
        "-b", "--batch",
        action="store_true",
        help="Process all PDFs in the books directory (default: books/)"
    )
    parser.add_argument(
        "--books-dir",
        default=DEFAULT_BOOKS_DIR,
        help=f"Directory containing PDF files for batch processing (default: {DEFAULT_BOOKS_DIR})"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output path: file path for single PDF, or directory for batch mode (default: output/)"
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
    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="In batch mode, reprocess PDFs even if output file already exists"
    )

    args = parser.parse_args()

    if args.batch:
        output_dir = args.output if args.output else DEFAULT_OUTPUT_DIR
        process_batch(
            books_dir=args.books_dir,
            output_dir=output_dir,
            pages_per_chunk=args.pages_per_chunk,
            dpi=args.dpi,
            skip_existing=not args.no_skip
        )
    else:
        if args.pdf_path is None:
            parser.error("pdf_path is required unless using --batch mode")

        if args.output is None:
            pdf_name = Path(args.pdf_path).stem
            output_file = f"{DEFAULT_OUTPUT_DIR}/{pdf_name}.md"
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
