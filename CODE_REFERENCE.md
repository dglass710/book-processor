# Code Reference

This document summarizes the classes, functions and methods found in the repository `book-processor`. Each section lists the file followed by a brief description of every callable along with inputs, outputs and notable calls to other parts of the codebase.

## auto_process.py

### `main(timeout=None)`
Automates running `setup_environment.py` with predefined responses. It sets environment variables, spawns a subprocess to run the setup script and forwards input via `stdin`. A background thread prints real-time output. If a timeout is provided the process is terminated when the limit is reached.
- **Inputs:** optional `timeout` in seconds.
- **Outputs:** return code from the subprocess (`int`).
- **Calls:** `subprocess.Popen` to launch `setup_environment.py`.

## main.py

### `check_dependencies()`
Verifies availability of required tools (`tesseract`, `ddjvu`, `ebook-convert`) and Python packages (`PyPDF2`, `PyMuPDF`).
- **Outputs:** `(bool success, list missing)`.
- **Calls:** `check_command_exists` from `utils.file_utils`.

### `install_dependencies_guide(missing_dependencies)`
Returns instructions for installing any missing dependencies.
- **Inputs:** list of missing dependency names.
- **Outputs:** instruction string.
- **Calls:** `get_platform` from `utils.file_utils`.

### `prompt_for_input_file()`
Prompts the user (or reads `BOOK_PROCESSOR_INPUT_FILE`) for the path of the book file and validates it.
- **Outputs:** `(file_path, file_type)` where `file_type` is one of `pdf`, `djvu`, `epub`, `mobi`.
- **Calls:** `normalize_path`, `validate_input_file`, `validate_pdf_integrity`, `validate_djvu_integrity`.

### `prompt_for_page_offset()`
Asks for a numeric page offset for books using Roman numeral preambles.
- **Outputs:** `int` offset value.

### `prompt_for_chapter_pages(max_page, page_offset=0)`
Collects chapter start pages and the last chapter end page.
- **Inputs:** `max_page` (highest PDF page) and optional `page_offset`.
- **Outputs:** `(list start_pages, int last_page)`.
- **Calls:** `validate_page_numbers` from `utils.validation`.

### `prompt_for_chapter_titles(chapter_count)`
Requests a title for each chapter.
- **Inputs:** `chapter_count`.
- **Outputs:** list of titles.

### `prompt_for_chapter_descriptions(chapter_count, titles)`
Requests a short description for each chapter.
- **Inputs:** `chapter_count`, list of chapter `titles`.
- **Outputs:** list of descriptions.

### `main()`
Coordinates the overall book processing workflow: dependency checks, file conversion, extraction, OCR, chapter creation, combination and final archive.
- **Calls:** functions above plus utilities from `utils.*` and processors `FormatConverter`, `PDFExtractor`, `OCRProcessor`, `ChapterOrganizer`, `CombinedChapterOrganizer` and `create_zip_archive`.
- **Outputs:** exit status (`int`).

## monitor_files.py

### `count_files(directory)`
Returns the number of files in a directory, or an error string if the directory cannot be read.

### `main()`
Monitors two subdirectories (`images` and `text`) under a book directory and prints their file counts every few seconds.

## processors/converter.py

### Class `FormatConverter`
Handles conversion between formats.
- **`__init__()`** – checks for the availability of `ddjvu` and `ebook-convert`.
- **`check_dependencies()`** – confirms required commands are present.
- **`install_dependencies_guide()`** – returns installation instructions for missing tools.
- **`ebook_to_pdf(ebook_path, output_pdf_path)`** – uses `ebook-convert` to convert EPUB/MOBI to PDF.
- **`djvu_to_pdf(djvu_path, output_pdf_path, quality=50)`** – uses `ddjvu` to convert DJVU to PDF.

## processors/extractor.py

### `_extract_page_worker(args)`
Helper for parallel image extraction with PyMuPDF.

### Class `PDFExtractor`
- **`__init__()`** – verifies PyMuPDF availability.
- **`check_dependencies()`** – returns whether PyMuPDF is installed.
- **`install_dependencies_guide()`** – installation help for PyMuPDF.
- **`get_pdf_info(pdf_path)`** – returns metadata and page count using `PyPDF2`.
- **`extract_images_with_pymupdf()`** – sequential extraction of images with PyMuPDF.
- **`extract_images_parallel()`** – parallel extraction using `ProcessPoolExecutor` and `_extract_page_worker`.
- **`extract_images()`** – wrapper calling `extract_images_parallel`.
- **`extract_text_per_page()`** – extracts text from each PDF page with PyMuPDF.

## processors/ocr.py

### `_process_image_worker(args)`
Worker used by `process_images_parallel` to invoke `OCRProcessor.process_image` in a separate process.

### Class `OCRProcessor`
- **`__init__()`** – checks for the `tesseract` command.
- **`check_dependencies()`** – verifies Tesseract availability.
- **`install_dependencies_guide()`** – provides install instructions.
- **`get_tesseract_version()`** – returns version string if available.
- **`get_available_languages()`** – lists languages supported by the OCR installation.
- **`process_image(image_path, output_path, language='eng', config='')`** – runs OCR on a single image via `subprocess`.
- **`process_images(image_paths, output_dir, language='eng', config='', prefix='page')`** – sequential OCR over multiple images; uses `process_image`.
- **`process_images_parallel(image_paths, output_dir, language='eng', config='', prefix='page', max_workers=None)`** – parallel OCR using `_process_image_worker` with `ProcessPoolExecutor`.

## processors/organizer.py

### Class `ChapterOrganizer`
- **`__init__()`** – empty initializer.
- **`parse_chapter_locations(chapter_starts, chapter_titles=None, max_page=None, page_offset=0)`** – builds chapter dictionaries with start/end page data and optional page offset handling.
- **`process_chapter(chapter, text_dir, output_dir)`** – concatenates individual page text files into a chapter file with headers and page markers.
- **`process_chapters(chapters, text_dir, output_dir)`** – iterates over chapter definitions calling `process_chapter` for each.

### Class `CombinedChapterOrganizer`
- **`__init__(max_combined_files=15)`** – sets the maximum number of combined files.
- **`optimize_chapter_groups(chapters)`** – groups chapters to balance file sizes.
- **`create_combined_file(group, chapters, chapters_dir, output_dir)`** – merges multiple chapter files into a single combined file and writes range headers.
- **`create_combined_files(groups, chapters, chapters_dir, output_dir)`** – loops over groups to create all combined files using `create_combined_file`.
- **`create_index_file(groups, chapters, output_dir, book_title=None)`** – generates an index mapping chapters to combined files.
- **`create_instructions_file(output_dir, book_title, num_combined_files, num_chapters, has_page_offset=False)`** – writes an LLM usage guide referencing the combined files and chapters.

## run_book_processor.py

Runs `main()` from `main.py` after adding the repository root to `sys.path`.

## setup_environment.py

### `check_dependency(name, command)`
Tests whether an external command exists by trying common version flags.

### `main()`
Adds Tesseract and DjVuLibre directories to `PATH`, checks their availability with `check_dependency`, and finally imports and runs `main` from `main.py`.

## utils/file_utils.py

Functions providing cross-platform file utilities:
- **`get_platform()`** – returns `'windows'`, `'macos'`, or `'linux'`.
- **`normalize_path(path)`** – normalizes a filesystem path.
- **`ensure_dir(directory)`** – creates a directory if missing.
- **`get_basename(filepath, with_extension=False)`** – extracts the base filename.
- **`check_file_exists(filepath)`** – verifies that a path points to an existing file.
- **`check_file_readable(filepath)`** – verifies file exists and is readable.
- **`open_file_with_default_app(filepath)`** – opens a file using the OS default application.
- **`create_project_structure(base_dir, book_name)`** – creates a unique project directory with subfolders (`images`, `text`, `chapters`, `combined`).
- **`check_command_exists(command)`** – checks availability of a system command using `where`/`which`.
- **`create_zip_archive(source_dir, output_file, files_to_include=None)`** – builds a zip file from a directory or specified files.

## utils/progress.py

### Class `ProgressTracker`
Simple textual progress bar for long operations.
- Methods: `__init__`, `start`, `update`, `finish`, `_display_progress`, `_format_time`.

### Class `StepProgress`
Tracks progress through multiple named steps.
- Methods: `__init__`, `start`, `start_step`, `end_step`, `finish`, `_format_time`.

## utils/validation.py

Validation helpers:
- **`validate_input_file(filepath)`** – checks existence, readability and extension.
- **`validate_page_numbers(page_numbers, min_page=1, max_pages=None)`** – verifies ascending order and range.
- **`validate_pdf_integrity(pdf_path)`** – ensures a PDF is readable using `PyPDF2`.
- **`validate_djvu_integrity(djvu_path)`** – validates DJVU files using `djvused`.
- **`parse_user_input(prompt, validation_func=None, default=None, attempts=3)`** – prompts the user with optional validation.

## monitor_files.py (again)
See above for its two simple functions.

---
