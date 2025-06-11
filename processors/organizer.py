"""
Organizer module for organizing text files into chapters and combined chapters
"""
import os
import re
import math
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  
from utils.progress import ProgressTracker


class ChapterOrganizer:
    """
    Organize text files into chapters and combined chapters
    """
    def __init__(self):
        pass
    
    def parse_chapter_locations(self, chapter_starts, chapter_titles=None, max_page=None, page_offset=0):
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
        
        # Create chapter dictionaries
        for i, start_page in enumerate(chapter_starts):
            chapter_num = i + 1
            
            # Calculate book page numbers
            book_start_page = start_page - page_offset if page_offset > 0 else start_page
            
            # Set title
            title = f"Chapter {chapter_num}"
            if chapter_titles and i < len(chapter_titles):
                if chapter_titles[i]:
                    title = chapter_titles[i]
            
            # Create chapter dictionary
            chapter = {
                'number': chapter_num,
                'title': title,
                'start_page': start_page,  # PDF page number
                'book_start_page': book_start_page,  # Book page number
                'end_page': None,  # Will be set later (PDF page number)
                'book_end_page': None,  # Will be set later (book page number)
                'page_offset': page_offset  # Store the offset
            }
            
            # Add end page for previous chapter
            if i > 0:
                chapters[i-1]['end_page'] = start_page - 1
                chapters[i-1]['book_end_page'] = book_start_page - 1 if page_offset > 0 else start_page - 1
                
            chapters.append(chapter)
            
        # Set end page for last chapter
        if chapters and max_page:
            chapters[-1]['end_page'] = max_page
            chapters[-1]['book_end_page'] = max_page - page_offset if page_offset > 0 else max_page
            
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
        chapter_num = chapter['number']
        start_page = chapter['start_page']  # PDF page number
        end_page = chapter['end_page']      # PDF page number
        title = chapter['title']
        
        # Get book page numbers if available
        book_start_page = chapter.get('book_start_page', start_page)
        book_end_page = chapter.get('book_end_page', end_page)
        page_offset = chapter.get('page_offset', 0)
        
        # Prepare output file
        output_filename = f"chapter_{chapter_num:02d}.txt"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Open output file
            with open(output_path, 'w', encoding='utf-8') as outfile:
                # Write chapter header
                outfile.write('='*80 + '\n')
                outfile.write(f"{title}\n")
                
                # Display page numbers - show both book pages and PDF pages if there's an offset
                if page_offset > 0:
                    outfile.write(f"Book Pages {book_start_page}-{book_end_page} (PDF Pages {start_page}-{end_page})\n")
                else:
                    outfile.write(f"Pages {start_page}-{end_page}\n")
                    
                outfile.write('='*80 + '\n\n')
                
                # Process each page
                char_count = 0
                for page_num in range(start_page, end_page + 1):
                    page_filename = f"page-{page_num:03d}.txt"
                    page_path = os.path.join(text_dir, page_filename)
                    
                    # Calculate book page number if there's an offset
                    if page_offset > 0:
                        book_page_num = page_num - page_offset
                        # Write page header with both numbering systems
                        outfile.write('\n' + '='*40 + '\n')
                        outfile.write(f"[BEGIN PAGE {page_num} (Book Page {book_page_num})]\n")
                        outfile.write('='*40 + '\n\n')
                    else:
                        # Write page header with just PDF page number
                        outfile.write('\n' + '='*40 + '\n')
                        outfile.write(f"[BEGIN PAGE {page_num}]\n")
                        outfile.write('='*40 + '\n\n')
                    
                    # Write page content
                    try:
                        with open(page_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                            char_count += len(content)
                    except FileNotFoundError:
                        outfile.write(f"[WARNING: Page {page_num} content not found]\n")
                    except UnicodeDecodeError:
                        # Try with different encoding if UTF-8 fails
                        try:
                            with open(page_path, 'r', encoding='latin-1') as infile:
                                content = infile.read()
                                outfile.write(content)
                                char_count += len(content)
                        except Exception:
                            outfile.write(f"[WARNING: Page {page_num} content could not be decoded]\n")
                    
                    # Write page footer
                    outfile.write('\n\n' + '='*40 + '\n')
                    if page_offset > 0:
                        book_page_num = page_num - page_offset
                        outfile.write(f"[END PAGE {page_num} (Book Page {book_page_num})]\n")
                    else:
                        outfile.write(f"[END PAGE {page_num}]\n")
                    outfile.write('='*40 + '\n')
            
            return True, f"Successfully processed chapter {chapter_num}", output_path, char_count
        
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
                chapter['char_count'] = char_count
                chapter['output_path'] = output_path
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
                processed_chapters
            )
        
        return True, f"Successfully processed all {len(chapters)} chapters", processed_chapters


class CombinedChapterOrganizer:
    """
    Organize chapters into combined chapter files
    """
    def __init__(self, max_combined_files=15):
        self.max_combined_files = max_combined_files
    
    def optimize_chapter_groups(self, chapters):
        """
        Optimize chapter grouping to minimize the largest file size
        while keeping adjacent chapters together and limiting the total number of files
        
        Args:
            chapters: List of chapter dictionaries with char_count
            
        Returns:
            list: List of chapter group dictionaries
        """
        if not chapters:
            return []
        
        # If we have fewer chapters than max_combined_files, each chapter gets its own file
        if len(chapters) <= self.max_combined_files:
            return [{'file': f"{i+1:02d}", 'chapters': [ch['number']], 'desc': f"Chapter {ch['number']}"} 
                   for i, ch in enumerate(chapters)]
        
        # Create a mapping from chapter number to index in the chapters list
        chapter_map = {ch['number']: i for i, ch in enumerate(chapters)}
        
        # Calculate total character count
        total_chars = sum(ch['char_count'] for ch in chapters)
        
        # Estimate target size per file (if evenly distributed)
        target_size = total_chars / min(self.max_combined_files, len(chapters))
        
        # Initialize groups
        groups = []
        current_group = []
        current_size = 0
        
        for ch in chapters:
            # If adding this chapter would exceed target size and we already have chapters in the group
            # and we haven't reached the maximum number of groups yet
            if (current_size + ch['char_count'] > target_size * 1.5 and 
                current_group and 
                len(groups) < self.max_combined_files - 1):
                
                # Save current group and start a new one
                if current_group:
                    groups.append(current_group)
                current_group = [ch['number']]
                current_size = ch['char_count']
            else:
                # Add chapter to current group
                current_group.append(ch['number'])
                current_size += ch['char_count']
        
        # Add the last group if it's not empty
        if current_group:
            groups.append(current_group)
        
        # Format the groups
        formatted_groups = []
        for i, group in enumerate(groups):
            # Create chapter range description
            if len(group) == 1:
                desc = f"Chapter {group[0]}"
            else:
                desc = f"Chapters {group[0]}–{group[-1]}"
            
            formatted_groups.append({
                'file': f"{i+1:02d}",
                'chapters': group,
                'desc': desc
            })
        
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
        file_num = group['file']
        chapter_numbers = group['chapters']
        description = group['desc']
        
        # Create output filename
        output_filename = f"combined_{file_num}.txt"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Get chapters in this group
            group_chapters = [ch for ch in chapters if ch['number'] in chapter_numbers]
            
            # Sort chapters by number
            group_chapters.sort(key=lambda x: x['number'])
            
            # Calculate page range (PDF page numbers)
            start_page = min(ch['start_page'] for ch in group_chapters)
            end_page = max(ch['end_page'] for ch in group_chapters)
            
            # Check if we have book page numbers (with offset)
            has_offset = any(ch.get('page_offset', 0) > 0 for ch in group_chapters)
            
            if has_offset:
                # Calculate book page range
                book_start_page = min(ch.get('book_start_page', ch['start_page']) for ch in group_chapters)
                book_end_page = max(ch.get('book_end_page', ch['end_page']) for ch in group_chapters)
                
                # Open output file
                with open(output_path, 'w', encoding='utf-8') as outfile:
                    # Write combined file header with both page numbering systems
                    outfile.write(f"{output_filename} - {description} (Book Pages {book_start_page}-{book_end_page}, PDF Pages {start_page}-{end_page})\n\n")
            else:
                # Open output file
                with open(output_path, 'w', encoding='utf-8') as outfile:
                    # Write combined file header with just PDF page numbers
                    outfile.write(f"{output_filename} - {description} (Pages {start_page}-{end_page})\n\n")
                
                # Process each chapter
                for chapter in group_chapters:
                    chapter_num = chapter['number']
                    chapter_filename = f"chapter_{chapter_num:02d}.txt"
                    chapter_path = os.path.join(chapters_dir, chapter_filename)
                    
                    try:
                        with open(chapter_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                            outfile.write("\n\n")
                    except FileNotFoundError:
                        outfile.write(f"[WARNING: Chapter {chapter_num} content not found]\n\n")
                    except UnicodeDecodeError:
                        # Try with different encoding if UTF-8 fails
                        try:
                            with open(chapter_path, 'r', encoding='latin-1') as infile:
                                content = infile.read()
                                outfile.write(content)
                                outfile.write("\n\n")
                        except Exception:
                            outfile.write(f"[WARNING: Chapter {chapter_num} content could not be decoded]\n\n")
            
            return True, f"Successfully created combined file {output_filename}", output_path
        
        except Exception as e:
            return False, f"Error creating combined file {output_filename}: {str(e)}", None
    
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
                output_files
            )
        
        return True, f"Successfully created all {len(groups)} combined files", output_files
    
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
            
            # Create a mapping from chapter number to chapter info
            chapter_map = {ch['number']: ch for ch in chapters}
            
            # Open index file
            with open(index_path, 'w', encoding='utf-8') as outfile:
                # Write index header
                if book_title:
                    outfile.write(f"{book_title} - Combined Chapter Files Index\n")
                else:
                    outfile.write("Combined Chapter Files Index\n")
                
                outfile.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}\n\n")
                
                # Process each group
                for group in groups:
                    file_num = group['file']
                    chapter_numbers = group['chapters']
                    description = group['desc']
                    
                    # Get chapters in this group
                    group_chapters = [chapter_map[num] for num in chapter_numbers if num in chapter_map]
                    
                    # Calculate page range (PDF page numbers)
                    if group_chapters:
                        start_page = min(ch['start_page'] for ch in group_chapters)
                        end_page = max(ch['end_page'] for ch in group_chapters)
                        
                        # Check if we have book page numbers (with offset)
                        has_offset = any(ch.get('page_offset', 0) > 0 for ch in group_chapters)
                        
                        if has_offset:
                            # Calculate book page range
                            book_start_page = min(ch.get('book_start_page', ch['start_page']) for ch in group_chapters)
                            book_end_page = max(ch.get('book_end_page', ch['end_page']) for ch in group_chapters)
                            
                            # Write group header with both page numbering systems
                            outfile.write(f"combined_{file_num}.txt - {description} (Book Pages {book_start_page}-{book_end_page}, PDF Pages {start_page}-{end_page})\n")
                        else:
                            # Write group header with just PDF page numbers
                            outfile.write(f"combined_{file_num}.txt - {description} (Pages {start_page}-{end_page})\n")
                        
                        # Write chapter details
                        for chapter in sorted(group_chapters, key=lambda x: x['number']):
                            chapter_num = chapter['number']
                            chapter_title = chapter['title']
                            chapter_start = chapter['start_page']  # PDF page number
                            chapter_end = chapter['end_page']      # PDF page number
                            
                            # Get book page numbers if available
                            page_offset = chapter.get('page_offset', 0)
                            book_start_page = chapter.get('book_start_page', chapter_start)
                            book_end_page = chapter.get('book_end_page', chapter_end)
                            
                            # Extract chapter title without number if possible
                            title_match = re.search(r'Chapter\s+\d+[:\s]+(.+)', chapter_title)
                            clean_title = title_match.group(1) if title_match else chapter_title
                            
                            # Display page numbers - show both book pages and PDF pages if there's an offset
                            if page_offset > 0:
                                outfile.write(f"    {chapter_title} (Book p.{book_start_page}-{book_end_page}, PDF p.{chapter_start}-{chapter_end})\n")
                            else:
                                outfile.write(f"    {chapter_title} (p.{chapter_start}-{chapter_end})\n")
                            
                            # If chapter has a description, add it
                            if 'description' in chapter and chapter['description']:
                                desc_lines = chapter['description'].split('\n')
                                for line in desc_lines:
                                    outfile.write(f"        {line}\n")
                            
                        outfile.write("\n")
            
            return True, f"Successfully created index file", index_path
        
        except Exception as e:
            return False, f"Error creating index file: {str(e)}", None
    
    def create_instructions_file(self, output_dir, book_title, num_combined_files, num_chapters, has_page_offset=False):
        """
        Create an instructions file for LLM consumption
        
        Args:
            output_dir: Directory to save instructions file
            book_title: Title of the book
            num_combined_files: Number of combined files
            num_chapters: Number of chapters
            
        Returns:
            tuple: (success, message, instructions_path)
        """
        # Create output filename
        instructions_path = os.path.join(output_dir, "instructions.txt")
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Open instructions file
            with open(instructions_path, 'w', encoding='utf-8') as outfile:
                outfile.write(f"You are a subject matter expert on *{book_title}*, using {num_combined_files} uploaded text files (combined_01.txt to combined_{num_combined_files:02d}.txt), each containing one or more of the book's {num_chapters} chapters, and an index file (index.txt) mapping chapters to their respective files.\n\n")
                outfile.write("You must follow this non-negotiable, three-step workflow for every query:\n\n")
                outfile.write("1. **READ index.txt FIRST**: Immediately open index.txt to identify the correct combined file(s) and chapter(s) for the user's query using keywords, chapter titles, or subtopics. Never search other files without this mapping. Example: \"trichomes\" → Chapter 8 → combined_02.txt; \"greenhouses\" → Chapter 11 → combined_03.txt.\n")
                outfile.write("2. **SEARCH ONLY THE RELEVANT FILES**: Search strictly within the identified file(s) and chapter(s), using [BEGIN PAGE X] and [END PAGE X] markers to locate content.\n")
                # Different citation format instructions based on whether there's a page offset
                if has_page_offset:
                    outfile.write("3. **RESPOND WITH PRECISE DUAL-FORMAT CITATIONS**: Quote or paraphrase only from the relevant chapter(s), citing the exact file and the narrowest possible page range that directly covers the topic. You MUST include BOTH page numbering systems in every citation (e.g., \"Source: combined_02.txt, Book Pages 75-77, PDF Pages 85-87\"). Broad or generic page citations are not acceptable.\n\n")
                else:
                    outfile.write("3. **RESPOND WITH PRECISE CITATIONS**: Quote or paraphrase only from the relevant chapter(s), citing the exact file and the narrowest possible page range that directly covers the topic (e.g., \"Source: combined_02.txt, Pages 85–87\"). Broad or generic page citations are not acceptable.\n\n")
                outfile.write("**Diagnostic Output Requirement:** Every response must include the statement: \"Index consulted: [list of file(s) and chapter(s) identified, e.g., combined_02.txt, Chapter 8].\"\n\n")
                outfile.write("**What You Must Not Do:**\n")
                outfile.write("- Do NOT use external information or make assumptions not present in the files.\n")
                outfile.write("- Do NOT reference visuals or diagrams, as this is a text-only source.\n")
                outfile.write("- Do NOT cite incorrect files/chapters (e.g., combined_10.txt for greenhouses).\n")
                # Different citation warning based on whether there's a page offset
                if has_page_offset:
                    outfile.write("- Do NOT use overly broad citations (e.g., Book Pages 75-98, PDF Pages 85-108). Use only the minimal span of pages necessary.\n")
                    outfile.write("- Do NOT omit either page numbering system in citations. ALWAYS include both Book Pages and PDF Pages.\n\n")
                else:
                    outfile.write("- Do NOT use overly broad citations (e.g., Pages 85–98). Use only the minimal span of pages necessary.\n\n")
                outfile.write("**Tasks Supported:**\n")
                outfile.write("- Answer cultivation and plant care questions with pinpoint accuracy.\n")
                outfile.write("- Summarize chapters or topics clearly.\n")
                outfile.write("- Create flashcards or multiple-choice quizzes with source citations.\n")
                outfile.write("- Explain techniques (e.g., trichomes, hydroponics) using clear language from the book.\n")
                outfile.write(f"- If a topic is not found in the {num_chapters} chapters, state: \"This information is not covered in {book_title}.\"\n\n")
                outfile.write("**Document Structure Reminder:**\n")
                outfile.write("- File headers show chapter ranges.\n")
                outfile.write("- Chapter markers specify chapter number, title, and page range.\n")
                
                # Add information about page numbering systems if there's a page offset
                if has_page_offset:
                    outfile.write("- This book uses two page numbering systems: Book Pages (as printed in the book) and PDF Pages (as shown in the PDF file).\n")
                    outfile.write("- Page markers in the text show both systems: [BEGIN PAGE 25 (Book Page 15)] means PDF page 25, which is page 15 in the book.\n")
                    outfile.write("- When citing pages, you MUST ALWAYS include both numbering systems for clarity (e.g., 'Book Pages 15-20, PDF Pages 25-30'). This is a strict requirement for all citations.\n")
                    outfile.write("- Pages are clearly marked: [BEGIN PAGE X (Book Page Y)] / [END PAGE X (Book Page Y)].\n\n")
                else:
                    outfile.write("- Pages are clearly marked: [BEGIN PAGE X] / [END PAGE X].\n\n")
                
                if has_page_offset:
                    outfile.write(f"Your mission is to deliver fully accurate, strictly sourced, index-confirmed responses from *{book_title}*. Always use the narrowest page range directly covering the topic and ALWAYS cite both Book Pages and PDF Pages in every citation.")
                else:
                    outfile.write(f"Your mission is to deliver fully accurate, strictly sourced, index-confirmed responses from *{book_title}*. Always use the narrowest page range directly covering the topic.")
            
            return True, f"Successfully created instructions file", instructions_path
        
        except Exception as e:
            return False, f"Error creating instructions file: {str(e)}", None
