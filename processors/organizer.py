"""
Organizer module for organizing text files into chapters and combined chapters
"""

import os
import sys
from datetime import datetime
from typing import Optional, Tuple

from utils.progress import ProgressTracker

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class ChapterOrganizer:
    """
    Organize text files into chapters and combined chapters
    """

    def __init__(self):
        pass

    def parse_chapter_locations(
        self, chapter_starts, chapter_titles=None, max_page=None, page_offset=0
    ):
        """
        Parse chapter start pages and create chapter information

        Args:
            chapter_starts: List of chapter start pages (PDF page numbers)
            chapter_titles: List of chapter titles (optional)
            max_page: Maximum page number (PDF page number, optional)
            page_offset: Offset between book pages and PDF pages (optional)

        Returns:
            list: List of chapter dictionaries with start and end pages
        """
        if not chapter_starts:
            return []

        chapters = []

        # Sort chapter starts to ensure they're in order
        chapter_starts = sorted(chapter_starts)

        # Add front matter if there's content before first chapter
        if chapter_starts[0] > 1:
            front_matter = {
                "number": 0,
                "title": "Front Matter",
                "start_page": 1,  # PDF page number
                "book_start_page": (
                    1 if page_offset <= 0 else 1 - page_offset
                ),  # Book page number
                "end_page": chapter_starts[0] - 1,  # PDF page number
                "book_end_page": (
                    (chapter_starts[0] - 1) - page_offset
                    if page_offset > 0
                    else chapter_starts[0] - 1
                ),
                "page_offset": page_offset,  # Store the offset
            }
            chapters.append(front_matter)

        # Create chapter dictionaries
        for i, start_page in enumerate(chapter_starts):
            chapter_num = i + 1

            # Calculate book page numbers
            book_start_page = (
                start_page - page_offset if page_offset > 0 else start_page
            )

            # Set title
            title = f"Chapter {chapter_num}"
            if chapter_titles and i < len(chapter_titles):
                if chapter_titles[i]:
                    title = chapter_titles[i]

            # Create chapter dictionary
            chapter = {
                "number": chapter_num,
                "title": title,
                "start_page": start_page,  # PDF page number
                "book_start_page": book_start_page,  # Book page number
                "end_page": None,  # Will be set later (PDF page number)
                "book_end_page": None,  # Will be set later (book page number)
                "page_offset": page_offset,  # Store the offset
            }

            # Add end page for previous chapter if it's a regular chapter
            if i > 0:
                chapters[-1]["end_page"] = start_page - 1
                chapters[-1]["book_end_page"] = (
                    book_start_page - 1 if page_offset > 0 else start_page - 1
                )

            chapters.append(chapter)

        # Set end page for last chapter
        if chapters and max_page:
            last_chapter_end = max_page - 1  # Leave room for back matter
            chapters[-1]["end_page"] = last_chapter_end
            chapters[-1]["book_end_page"] = (
                last_chapter_end - page_offset if page_offset > 0 else last_chapter_end
            )

            # Add back matter if there's content after last chapter
            if max_page > last_chapter_end:
                back_matter = {
                    "number": len(chapter_starts) + 1,
                    "title": "Back Matter",
                    "start_page": last_chapter_end + 1,  # PDF page number
                    "book_start_page": (
                        (last_chapter_end + 1) - page_offset
                        if page_offset > 0
                        else last_chapter_end + 1
                    ),
                    "end_page": max_page,  # PDF page number
                    "book_end_page": (
                        max_page - page_offset if page_offset > 0 else max_page
                    ),
                    "page_offset": page_offset,  # Store the offset
                }
                chapters.append(back_matter)

        return chapters

    def process_chapter(self, chapter, text_dir, output_dir):
        """
        Process a chapter by combining page text files

        Args:
            chapter: Chapter dictionary with number, title, start_page, end_page
            text_dir: Directory containing page text files
            output_dir: Directory to save chapter text files

        Returns:
            tuple: (success, message, output_path, char_count)
        """
        chapter_num = chapter["number"]
        start_page = chapter["start_page"]  # PDF page number
        end_page = chapter["end_page"]  # PDF page number
        title = chapter["title"]

        # Get book page numbers if available
        book_start_page = chapter.get("book_start_page", start_page)
        book_end_page = chapter.get("book_end_page", end_page)
        page_offset = chapter.get("page_offset", 0)

        # Prepare output file
        output_filename = f"chapter_{chapter_num:02d}.txt"
        output_path = os.path.join(output_dir, output_filename)

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Open output file
            with open(output_path, "w", encoding="utf-8") as outfile:
                # Write chapter header
                outfile.write("=" * 80 + "\n")
                outfile.write(f"{title}\n")

                # Display page numbers - show both book pages and PDF pages if there's an offset
                if page_offset > 0:
                    outfile.write(
                        f"Book Pages {book_start_page}-{book_end_page} (PDF Pages {start_page}-{end_page})\n"
                    )
                else:
                    outfile.write(f"Pages {start_page}-{end_page}\n")

                outfile.write("=" * 80 + "\n\n")

                # Process each page
                char_count = 0
                for page_num in range(start_page, end_page + 1):
                    page_filename = f"page-{page_num:03d}.txt"
                    page_path = os.path.join(text_dir, page_filename)

                    # Calculate book page number if there's an offset
                    if page_offset > 0:
                        book_page_num = page_num - page_offset
                        # Write page header with both numbering systems
                        outfile.write("\n" + "=" * 40 + "\n")
                        outfile.write(
                            f"[BEGIN PAGE {page_num} (Book Page {book_page_num})]\n"
                        )
                        outfile.write("=" * 40 + "\n\n")
                    else:
                        # Write page header with just PDF page number
                        outfile.write("\n" + "=" * 40 + "\n")
                        outfile.write(f"[BEGIN PAGE {page_num}]\n")
                        outfile.write("=" * 40 + "\n\n")

                    # Write page content
                    try:
                        with open(page_path, "r", encoding="utf-8") as infile:
                            content = infile.read()
                            outfile.write(content)
                            char_count += len(content)
                    except FileNotFoundError:
                        outfile.write(f"[WARNING: Page {page_num} content not found]\n")
                    except UnicodeDecodeError:
                        # Try with different encoding if UTF-8 fails
                        try:
                            with open(page_path, "r", encoding="latin-1") as infile:
                                content = infile.read()
                                outfile.write(content)
                                char_count += len(content)
                        except Exception:
                            outfile.write(
                                f"[WARNING: Page {page_num} content could not be decoded]\n"
                            )

                    # Write page footer
                    outfile.write("\n\n" + "=" * 40 + "\n")
                    if page_offset > 0:
                        book_page_num = page_num - page_offset
                        outfile.write(
                            f"[END PAGE {page_num} (Book Page {book_page_num})]\n"
                        )
                    else:
                        outfile.write(f"[END PAGE {page_num}]\n")
                    outfile.write("=" * 40 + "\n")

            return (
                True,
                f"Successfully processed chapter {chapter_num}",
                output_path,
                char_count,
            )

        except Exception as e:
            return False, f"Error processing chapter {chapter_num}: {str(e)}", None, 0

    def process_chapters(self, chapters, text_dir, output_dir):
        """
        Process all chapters

        Args:
            chapters: List of chapter dictionaries
            text_dir: Directory containing page text files
            output_dir: Directory to save chapter text files

        Returns:
            tuple: (success, message, processed_chapters)
        """
        if not chapters:
            return False, "No chapters to process", []

        processed_chapters = []
        failed_chapters = []

        # Start progress tracker
        progress = ProgressTracker(len(chapters), "Processing chapters").start()

        for i, chapter in enumerate(chapters):
            # Process chapter
            success, message, output_path, char_count = self.process_chapter(
                chapter, text_dir, output_dir
            )

            if success:
                # Add character count to chapter info
                chapter["char_count"] = char_count
                chapter["output_path"] = output_path
                processed_chapters.append(chapter)
            else:
                failed_chapters.append((chapter, message))

            # Update progress
            progress.update()

        progress.finish()

        # Report results
        if failed_chapters:
            failures = len(failed_chapters)
            return (
                len(processed_chapters) > 0,
                f"Chapter processing completed with {failures} failures out of {len(chapters)} chapters",
                processed_chapters,
            )

        return (
            True,
            f"Successfully processed all {len(chapters)} chapters",
            processed_chapters,
        )


class CombinedChapterOrganizer:
    """
    Organize chapters into combined chapter files
    """

    def __init__(self, max_combined_files=9):
        self.max_combined_files = max_combined_files

    def optimize_chapter_groups(self, chapters):
        """
        Optimize chapter grouping using dynamic programming to minimize the maximum file size
        while keeping adjacent chapters together and limiting the total number of files.

        This algorithm finds the optimal distribution of chapters that minimizes
        the largest combined file.

        Args:
            chapters: List of chapter dictionaries with char_count

        Returns:
            list: List of chapter group dictionaries
        """
        if not chapters:
            return []

        # If we have fewer chapters than max_combined_files, each chapter gets its own file
        if len(chapters) <= self.max_combined_files:
            return [
                {
                    "file": f"{i+1:02d}",
                    "chapters": [ch["number"]],
                    "desc": f"Chapter {ch['number']}",
                }
                for i, ch in enumerate(chapters)
            ]

        n = len(chapters)
        k = min(self.max_combined_files, n)  # Number of partitions

        # Create a prefix sum array for quick subarray sum calculation
        prefix_sum = [0]
        for ch in chapters:
            prefix_sum.append(prefix_sum[-1] + ch["char_count"])

        # dp[i][j] represents the minimum maximum subarray sum when
        # partitioning chapters[0...i-1] into j partitions
        dp = [[float("inf")] * (k + 1) for _ in range(n + 1)]

        # partition[i][j] tracks where to cut for reconstructing the solution
        partition = [[0] * (k + 1) for _ in range(n + 1)]

        # Base case: one partition for the first i chapters
        for i in range(1, n + 1):
            dp[i][1] = prefix_sum[i]

        # Fill the dp table
        for i in range(1, n + 1):
            for j in range(2, min(i + 1, k + 1)):
                for p in range(j - 1, i):
                    current_cost = max(dp[p][j - 1], prefix_sum[i] - prefix_sum[p])
                    if current_cost < dp[i][j]:
                        dp[i][j] = current_cost
                        partition[i][j] = p

        # Reconstruct the solution
        groups = []
        current = n
        remaining = k

        while current > 0 and remaining > 0:
            prev = partition[current][remaining]
            # Chapters from prev+1 to current form a group
            chapter_group = [
                chapters[i - 1]["number"] for i in range(prev + 1, current + 1)
            ]
            # We insert at the beginning because we're working backwards
            groups.insert(0, chapter_group)
            current = prev
            remaining -= 1

        # Format the groups
        formatted_groups = []
        for i, group in enumerate(groups):
            # Create chapter range description
            if len(group) == 1:
                desc = f"Chapter {group[0]}"
            else:
                desc = f"Chapters {group[0]}–{group[-1]}"

            formatted_groups.append(
                {"file": f"{i+1:02d}", "chapters": group, "desc": desc}
            )

        return formatted_groups

    def create_combined_file(self, group, chapters, chapters_dir, output_dir):
        """
        Create a combined chapter file

        Args:
            group: Group dictionary with file, chapters, desc
            chapters: List of chapter dictionaries
            chapters_dir: Directory containing chapter text files
            output_dir: Directory to save combined chapter files

        Returns:
            tuple: (success, message, output_path)
        """
        file_num = group["file"]
        chapter_numbers = group["chapters"]
        description = group["desc"]

        # Create output filename
        output_filename = f"combined_{file_num}.txt"
        output_path = os.path.join(output_dir, output_filename)

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Get chapters in this group
            group_chapters = [ch for ch in chapters if ch["number"] in chapter_numbers]

            # Sort chapters by number
            group_chapters.sort(key=lambda x: x["number"])

            # Calculate page range (PDF page numbers)
            start_page = min(ch["start_page"] for ch in group_chapters)
            end_page = max(ch["end_page"] for ch in group_chapters)

            # Check if we have book page numbers (with offset)
            has_offset = any(ch.get("page_offset", 0) > 0 for ch in group_chapters)

            if has_offset:
                # Calculate book page range
                book_start_page = min(
                    ch.get("book_start_page", ch["start_page"]) for ch in group_chapters
                )
                book_end_page = max(
                    ch.get("book_end_page", ch["end_page"]) for ch in group_chapters
                )

                # Open output file
                with open(output_path, "w", encoding="utf-8") as outfile:
                    # Write combined file header with both page numbering systems
                    outfile.write(
                        f"{output_filename} - {description} (Book Pages {book_start_page}-{book_end_page}, PDF Pages {start_page}-{end_page})\n\n"
                    )

                    # Process each chapter
                    for chapter in group_chapters:
                        chapter_num = chapter["number"]
                        chapter_filename = f"chapter_{chapter_num:02d}.txt"
                        chapter_path = os.path.join(chapters_dir, chapter_filename)

                        try:
                            with open(chapter_path, "r", encoding="utf-8") as infile:
                                content = infile.read()
                                outfile.write(content)
                                outfile.write("\n\n")
                        except FileNotFoundError:
                            outfile.write(
                                f"[WARNING: Chapter {chapter_num} content not found]\n\n"
                            )
                        except UnicodeDecodeError:
                            # Try with different encoding if UTF-8 fails
                            try:
                                with open(
                                    chapter_path, "r", encoding="latin-1"
                                ) as infile:
                                    content = infile.read()
                                    outfile.write(content)
                                    outfile.write("\n\n")
                            except Exception:
                                outfile.write(
                                    f"[WARNING: Chapter {chapter_num} content could not be decoded]\n\n"
                                )
            else:
                # Open output file
                with open(output_path, "w", encoding="utf-8") as outfile:
                    # Write combined file header with just PDF page numbers
                    outfile.write(
                        f"{output_filename} - {description} (Pages {start_page}-{end_page})\n\n"
                    )

                    # Process each chapter
                    for chapter in group_chapters:
                        chapter_num = chapter["number"]
                        chapter_filename = f"chapter_{chapter_num:02d}.txt"
                        chapter_path = os.path.join(chapters_dir, chapter_filename)

                        try:
                            with open(chapter_path, "r", encoding="utf-8") as infile:
                                content = infile.read()
                                outfile.write(content)
                                outfile.write("\n\n")
                        except FileNotFoundError:
                            outfile.write(
                                f"[WARNING: Chapter {chapter_num} content not found]\n\n"
                            )
                        except UnicodeDecodeError:
                            # Try with different encoding if UTF-8 fails
                            try:
                                with open(
                                    chapter_path, "r", encoding="latin-1"
                                ) as infile:
                                    content = infile.read()
                                    outfile.write(content)
                                    outfile.write("\n\n")
                            except Exception:
                                outfile.write(
                                    f"[WARNING: Chapter {chapter_num} content could not be decoded]\n\n"
                                )

            return (
                True,
                f"Successfully created combined file {output_filename}",
                output_path,
            )

        except Exception as e:
            return (
                False,
                f"Error creating combined file {output_filename}: {str(e)}",
                None,
            )

    def create_combined_files(self, groups, chapters, chapters_dir, output_dir):
        """
        Create all combined chapter files

        Args:
            groups: List of group dictionaries
            chapters: List of chapter dictionaries
            chapters_dir: Directory containing chapter text files
            output_dir: Directory to save combined chapter files

        Returns:
            tuple: (success, message, output_files)
        """
        if not groups or not chapters:
            return False, "No groups or chapters to process", []

        output_files = []
        failed_files = []

        # Start progress tracker
        progress = ProgressTracker(len(groups), "Creating combined files").start()

        for i, group in enumerate(groups):
            # Create combined file
            success, message, output_path = self.create_combined_file(
                group, chapters, chapters_dir, output_dir
            )

            if success:
                output_files.append((group, output_path))
            else:
                failed_files.append((group, message))

            # Update progress
            progress.update()

        progress.finish()

        # Report results
        if failed_files:
            failures = len(failed_files)
            return (
                len(output_files) > 0,
                f"Combined file creation completed with {failures} failures out of {len(groups)} files",
                output_files,
            )

        return (
            True,
            f"Successfully created all {len(groups)} combined files",
            output_files,
        )

    def create_index_file(self, groups, chapters, output_dir, book_title=None):
        """
        Create an index file listing all combined files and their contents

        Args:
            groups: List of group dictionaries
            chapters: List of chapter dictionaries
            output_dir: Directory to save index file
            book_title: Title of the book (optional)

        Returns:
            tuple: (success, message, index_path)
        """
        if not groups or not chapters:
            return False, "No groups or chapters to process", None

        # Create output filename
        index_path = os.path.join(output_dir, "index.txt")

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Open index file
            with open(index_path, "w", encoding="utf-8") as outfile:
                # Write index header
                if book_title:
                    outfile.write(f"{book_title} - Combined Chapter Files Index\n")
                else:
                    outfile.write("Combined Chapter Files Index\n")

                outfile.write(
                    f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
                )

                # Process each group
                for group in groups:
                    file_num = group["file"]
                    chapter_numbers = group["chapters"]
                    description = group["desc"]

                    # Get chapters in this group
                    group_chapters = [
                        ch for ch in chapters if ch["number"] in chapter_numbers
                    ]

                    # Calculate page range (PDF page numbers)
                    if group_chapters:
                        start_page = min(ch["start_page"] for ch in group_chapters)
                        end_page = max(ch["end_page"] for ch in group_chapters)

                        # Check if we have book page numbers (with offset)
                        has_offset = any(
                            ch.get("page_offset", 0) > 0 for ch in group_chapters
                        )

                        if has_offset:
                            # Calculate book page range
                            book_start_page = min(
                                ch.get("book_start_page", ch["start_page"])
                                for ch in group_chapters
                            )
                            book_end_page = max(
                                ch.get("book_end_page", ch["end_page"])
                                for ch in group_chapters
                            )

                            # Write group header with both page numbering systems
                            outfile.write(
                                (
                                    f"combined_{file_num}.txt - {description} "
                                    f"(Book Pages {book_start_page}-{book_end_page}, "
                                    f"PDF Pages {start_page}-{end_page})\n"
                                )
                            )
                        else:
                            # Write group header with just PDF page numbers
                            outfile.write(
                                f"combined_{file_num}.txt - {description} (Pages {start_page}-{end_page})\n"
                            )

                        # Write chapter details
                        for chapter in sorted(
                            group_chapters, key=lambda x: x["number"]
                        ):
                            _ = chapter["number"]  # Skip chapter number
                            chapter_title = chapter["title"]
                            chapter_start = chapter["start_page"]  # PDF page number
                            chapter_end = chapter["end_page"]  # PDF page number

                            # Get book page numbers if available
                            page_offset = chapter.get("page_offset", 0)
                            book_start_page = chapter.get(
                                "book_start_page", chapter_start
                            )
                            book_end_page = chapter.get("book_end_page", chapter_end)

                            # Display page numbers - show both book pages and PDF pages if there's an offset
                            if page_offset > 0:
                                outfile.write(
                                    f"    {chapter_title} (Book p.{book_start_page}-{book_end_page}, PDF p.{chapter_start}-{chapter_end})\n"
                                )
                            else:
                                outfile.write(
                                    f"    {chapter_title} (p.{chapter_start}-{chapter_end})\n"
                                )

                            # If chapter has a description, add it
                            if "description" in chapter and chapter["description"]:
                                desc_lines = chapter["description"].split("\n")
                                for line in desc_lines:
                                    outfile.write(f"        {line}\n")

                        outfile.write("\n")

            return True, "Successfully created index file", index_path

        except Exception as e:
            return False, f"Error creating index file: {str(e)}", None

    def create_instructions_file(
        self,
        output_dir: str,
        book_title: str,
        num_combined_files: int,
        num_chapters: int,
        has_page_offset: bool = False,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Create an instructions file for LLM consumption

        Args:
            output_dir: Directory to save instructions file
            book_title: Title of the book
            num_combined_files: Number of combined files
            num_chapters: Number of chapters
            has_page_offset: Whether the book has page offset numbering

        Returns:
            tuple: (success, message, instructions_path)
        """
        # Create output filename
        instructions_path = os.path.join(output_dir, "instructions.txt")

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Open instructions file
            with open(instructions_path, "w", encoding="utf-8") as outfile:
                # Write initial instructions
                outfile.write(
                    f"You are a subject matter expert on *{book_title}*, using {num_combined_files} uploaded text files "
                    f"(combined_01.txt to combined_{num_combined_files:02d}.txt), each containing one or more of "
                    f"the book's {num_chapters} chapters, and an index file (index.txt) mapping chapters to their "
                    f"respective files.\n\n"
                )

                # Write workflow steps
                outfile.write(
                    "You must follow this non-negotiable, three-step workflow for every query:\n\n"
                )
                outfile.write(
                    "1. **READ index.txt FIRST**: Immediately open index.txt to identify the correct chapter(s) "
                    "(and their combined file if needed) for the user's query using keywords, chapter titles, "
                    'or subtopics. Never search other files without this mapping. Example: "budget planning" → '
                    'Chapter 8 → combined_02.txt; "marketing" → Chapter 11 → combined_03.txt.\n'
                )
                outfile.write(
                    "2. **SEARCH ONLY THE RELEVANT CHAPTERS**: Search strictly within the identified chapter(s) "
                    "and corresponding file(s), using [BEGIN PAGE X] and [END PAGE X] markers to locate content.\n"
                )

                # Write citation format instructions based on page offset
                if has_page_offset:
                    outfile.write(
                        "3. **RESPOND WITH PRECISE DUAL-FORMAT CITATIONS**: Quote or paraphrase only from the relevant "
                        "chapter(s), citing the chapter and the narrowest possible page range that directly covers "
                        "the topic. You MUST include BOTH page numbering systems in every citation "
                        '(e.g., "Source: Chapter 8, Book Pages 75-77, PDF Pages 85-87"). '
                        "Broad or generic page citations are not acceptable.\n\n"
                    )
                else:
                    outfile.write(
                        "3. **RESPOND WITH PRECISE CITATIONS**: Quote or paraphrase only from the relevant chapter(s), "
                        "citing the chapter and the narrowest possible page range that directly covers the topic "
                        '(e.g., "Source: Chapter 8, Pages 85–87"). Broad or generic page citations are not acceptable.\n\n'
                    )

                # Write diagnostic output requirement
                outfile.write(
                    "**Diagnostic Output Requirement:** Every response must include the statement: "
                    '"Index consulted: [list of chapter(s) identified, e.g., Chapter 8]."\n\n'
                )

                # Write what not to do
                outfile.write("**What You Must Not Do:**\n")
                outfile.write(
                    "- Do NOT use external information or make assumptions not present in the files.\n"
                )
                outfile.write(
                    "- Do NOT reference visuals or diagrams, as this is a text-only source.\n"
                )
                outfile.write(
                    "- Do NOT cite incorrect chapters (e.g., citing Chapter 10 for marketing).\n"
                )
                # Different citation warning based on whether there's a page offset
                if has_page_offset:
                    outfile.write(
                        "- Do NOT use overly broad citations (e.g., Book Pages 75-98, PDF Pages 85-108). "
                        "Use only the minimal span of pages necessary.\n"
                    )
                    outfile.write(
                        "- Do NOT omit either page numbering system in citations. ALWAYS include both Book Pages and PDF Pages.\n\n"
                    )
                else:
                    outfile.write(
                        "- Do NOT use overly broad citations (e.g., Pages 75-98). "
                        "Use only the minimal span of pages necessary.\n\n"
                    )

                # Write supported tasks
                outfile.write("**Tasks Supported:**\n")
                outfile.write("- Answer questions with pinpoint accuracy.\n")
                outfile.write("- Summarize chapters or topics clearly.\n")
                outfile.write(
                    "- Create flashcards or multiple-choice quizzes with source citations.\n"
                )
                outfile.write(
                    "- Explain techniques or concepts using clear language from the text.\n"
                )
                outfile.write(
                    f'- If a topic is not found in the {num_chapters} chapters, state: "This information is not covered in {book_title}."\n\n'
                )

                # Write document structure reminder
                outfile.write("**Document Structure Reminder:**\n")
                outfile.write("- File headers show chapter ranges.\n")
                outfile.write(
                    "- Chapter markers specify chapter number, title, and page range.\n"
                )
                # Add information about page numbering systems if there's a page offset
                if has_page_offset:
                    outfile.write(
                        "- This book uses two page numbering systems: Book Pages (printed) and PDF Pages (file).\n"
                    )
                    outfile.write(
                        "- Page markers show: [BEGIN PAGE 25 (Book Page 15)] means PDF page 25 is page 15.\n"
                    )
                    outfile.write(
                        "- When citing pages, you MUST ALWAYS include both numbering systems "
                        "(e.g., 'Book Pages 15-20, PDF Pages 25-30'). This is required.\n"
                    )
                    outfile.write(
                        "- Pages are clearly marked: [BEGIN PAGE X (Book Page Y)] / [END PAGE X (Book Page Y)].\n\n"
                    )
                else:
                    outfile.write(
                        "- Pages are clearly marked: [BEGIN PAGE X] / [END PAGE X].\n\n"
                    )

                # Write mission statement
                if has_page_offset:
                    outfile.write(
                        f"Your mission is to deliver accurate, sourced responses from *{book_title}*. "
                        f"Use narrow page ranges and include both Book Pages and PDF Pages in citations."
                    )
                else:
                    outfile.write(
                        f"Your mission is to deliver accurate, sourced responses from *{book_title}*. "
                        f"Use narrow page ranges in citations."
                    )

                return True, "Successfully created instructions file", instructions_path

        except Exception as e:
            return False, f"Error creating instructions file: {str(e)}", None
