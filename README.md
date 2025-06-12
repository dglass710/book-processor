# Book Processor

A comprehensive Python tool to automate the workflow of converting DJVU/PDF files into organized directories with PNG and text files, then combining text files into chapters and groups optimized for LLM consumption.

## Recent Enhancements

- **Dual Page Numbering System**: Display both book page numbers and PDF page numbers in all output files when a page offset is used
- **macOS-like Directory Naming**: Create uniquely named directories with incremented suffixes (e.g., "Book Name (1)") when processing the same book multiple times
- **Automated Processing**: Scripts for automating the book processing workflow with predefined inputs
- **Parallel OCR Processing**: Utilize multiple CPU cores to speed up OCR on large books
- **Parallel PNG Extraction**: Create PNG pages faster using multiple CPU cores

## Features

- Convert DJVU files to PDF (using DjVuLibre's `ddjvu`)
- Extract PNG images from PDF (using PyMuPDF)
- Accelerated PNG extraction with parallel processing
- Perform OCR on images to extract text (using tesseract)
- Accelerated OCR with parallel processing
- Organize text files into chapters with proper formatting
- Group chapters into combined files optimizing for file size
- Create an index file for easy navigation
- Create instructions for LLM consumption
- Package everything into a ZIP archive

## Requirements

### External Dependencies

- **tesseract-ocr**: For OCR processing
- **djvulibre**: Provides the `ddjvu` tool for DJVU to PDF conversion

### Python Dependencies

- PyPDF2
- PyMuPDF

## Installation

1. Install external dependencies:

   **Windows:**
   - tesseract: Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - djvulibre: Download from [SourceForge](https://sourceforge.net/projects/djvu/)

   **macOS:**
   ```bash
   brew install tesseract djvulibre
   ```

   **Linux (Debian/Ubuntu):**
   ```bash
   sudo apt-get install tesseract-ocr djvulibre-bin
   ```

   **Linux (Fedora):**
   ```bash
   sudo dnf install tesseract djvulibre
   ```

2. Install Python dependencies:
   ```bash
   pip install PyPDF2 PyMuPDF
   ```

## Usage

Run the main script:

```bash
python main.py
```

The script will guide you through the following steps:

1. Select an input file (PDF or DJVU)
2. Convert DJVU to PDF if necessary
3. Open the PDF for reference
4. Enter chapter start pages
5. Provide chapter titles and descriptions
6. Process the book (extract images, OCR, organize chapters)
7. Create a ZIP archive with combined chapter files

## Output

The script creates the following directory structure:

```
[book_name]/
├── images/           # PNG images of each page
├── text/             # OCR text files for each page
├── chapters/         # Text files for each chapter
├── combined/         # Combined chapter files
│   ├── combined_01.txt
│   ├── combined_02.txt
│   ├── ...
│   ├── index.txt     # Index of combined files
│   └── instructions.txt  # Instructions for LLM
└── [book_name]_combined.zip  # ZIP archive of combined files
```

## LLM Integration

The generated ZIP file contains:
- Combined chapter text files
- An index file mapping chapters to combined files
- Instructions for LLMs on how to navigate and use the content

This format is optimized for LLMs to efficiently access and reference specific parts of the book.

## License

This project is open source and available under the MIT License.
