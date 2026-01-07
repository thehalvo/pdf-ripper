# PDF Ripper

A Python tool that extracts text from PDF files using OCR and saves it to a single markdown file.

## Requirements

- Python 3.8+
- Tesseract OCR (system dependency)

## Installation

### 1. Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

### 2. Install Python dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python pdf_ripper.py <pdf_path> [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `pdf_path` | Path to the input PDF file (required) |
| `-o, --output` | Output markdown file path (default: `output/<pdf_name>.md`) |
| `-p, --pages-per-chunk` | Number of pages per progress update (default: `10`) |
| `-d, --dpi` | DPI for rendering pages (default: `300`, higher = better quality but slower) |

### Examples

Process a PDF with default settings (outputs to `output/document.md`):
```bash
python pdf_ripper.py document.pdf
```

Specify a custom output file:
```bash
python pdf_ripper.py document.pdf -o extracted_text.md
```

Use lower DPI for faster processing (lower quality):
```bash
python pdf_ripper.py document.pdf -d 150
```

Use higher DPI for better quality (slower):
```bash
python pdf_ripper.py document.pdf -d 400
```

## Output

The tool creates a single markdown file containing all extracted text with:
- A header with the PDF filename
- Page count metadata
- Individual page headers (`## Page N`)
- The OCR-extracted text from each page

## Notes

- OCR is used because many PDFs have corrupted or non-standard text encoding
- Processing time depends on page count and DPI setting
- For a 3340-page PDF at 300 DPI, expect several hours of processing time
- Lower DPI (150-200) is faster but may reduce accuracy for small text
