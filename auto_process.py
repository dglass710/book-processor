#!/usr/bin/env python3
"""
Auto Process Script - Automate the book processing workflow with predefined inputs

This script runs the book processor with predefined inputs to avoid manual entry.
It sets the environment variable for the input file and feeds responses to stdin.
"""
import os
import sys
import subprocess

def main(timeout=None):
    """Main function to run the book processor with automated inputs
    
    Args:
        timeout: Optional timeout in seconds. If None, no timeout will be applied.
               Set to a positive number to enable timeout.
    """
    print("=" * 80)
    print("Auto Process Script - Running book processor with predefined inputs")
    print("=" * 80)
    
    # Define the input file path
    input_file = r"C:\Users\dglas\Dropbox\Books\2012 RTE Manual.pdf"
    
    # Set environment variables
    os.environ["BOOK_PROCESSOR_INPUT_FILE"] = input_file
    os.environ["PYTHONIOENCODING"] = "utf-8"  # Fix encoding issues
    
    # Define the responses to provide to stdin
    responses = [
        "y",  # Continue anyway? (y/N)
        "Responding to Emergencies: Comprehensive First Aid/CPR/AED by American Red Cross",  # Book title
        "23",  # Page offset
        "y",  # Is page offset correct?
        "3 17 27 45 67 93 125 155 167 177 203 219 243 261 275 295 315 333 351 371 383 405 419",  # Chapter start pages
        "y",  # Is chapter info correct?
        "If Not You . . . Who?",  # Chapter 1 title
        "Responding to an Emergency",  # Chapter 2 title
        "Before Giving Care",  # Chapter 3 title
        "The Human Body",  # Chapter 4 title
        "Checking the Person",  # Chapter 5 title
        "Cardiac Emergencies",  # Chapter 6 title
        "Breathing Emergencies",  # Chapter 7 title
        "Bleeding",  # Chapter 8 title
        "Shock",  # Chapter 9 title
        "Soft Tissue Injuries",  # Chapter 10 title
        "Musculoskeletal Injuries",  # Chapter 11 title
        "Injuries to the Extremities",  # Chapter 12 title
        "Injuries to the Head, Neck and Spine",  # Chapter 13 title
        "Injuries to the Chest, Abdomen and Pelvis",  # Chapter 14 title
        "Sudden Illnesses",  # Chapter 15 title
        "Poisoning",  # Chapter 16 title
        "Bites and Stings",  # Chapter 17 title
        "Substance Abuse and Misuse",  # Chapter 18 title
        "Heat-Related Illnesses and Cold-Related Emergencies",  # Chapter 19 title
        "Water-Related Emergencies",  # Chapter 20 title
        "Pediatric, Older Adult and Special Situations",  # Chapter 21 title
        "Emergency Childbirth",  # Chapter 22 title
        "Disaster, Remote and Wilderness Emergencies",  # Chapter 23 title
    ]
    
    # Add empty descriptions for each chapter
    # We need one description for each chapter
    chapter_descriptions = [""] * 23  # 23 empty strings for chapter descriptions
    responses.extend(chapter_descriptions)
    
    # Add extra empty responses for any additional prompts that might come up
    extra_responses = [""] * 10  # Add some extra empty responses just in case
    responses.extend(extra_responses)
    
    # Prepare the input string (join responses with newlines)
    input_str = "\n".join(responses)
    
    # Path to the setup_environment.py script
    setup_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup_environment.py")
    
    # Run the setup_environment.py script with the prepared input
    try:
        print(f"Running setup_environment.py with automated input...")
        print(f"Input file: {input_file}")
        print(f"Using {len(responses)} predefined responses")
        print("=" * 80)
        
        # Create environment with UTF-8 encoding
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        # Run the process with real-time output display
        process = subprocess.Popen(
            [sys.executable, setup_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Redirect stderr to stdout
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env
        )
        
        # Send all input at once
        process.stdin.write(input_str)
        process.stdin.close()
        
        # Read and display output in real-time with a timeout
        import time
        import threading
        
        # Flag to indicate if the process is still running
        running = True
        output_lines = []
        
        def read_output():
            while running:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    print(line.rstrip())
                    output_lines.append(line)
        
        # Start thread to read output
        output_thread = threading.Thread(target=read_output)
        output_thread.daemon = True
        output_thread.start()
        
        # Wait for process with optional timeout
        start_time = time.time()
        
        while process.poll() is None:
            if timeout is not None and time.time() - start_time > timeout:
                print(f"\nProcess timed out after {timeout} seconds. Terminating...")
                process.terminate()
                time.sleep(1)
                if process.poll() is None:
                    process.kill()
                break
            time.sleep(0.1)
        
        # Stop the output thread
        running = False
        output_thread.join(1)  # Wait for output thread to finish (max 1 second)
        
        # Get return code
        returncode = process.poll()
        
        # Check the return code
        if returncode != 0:
            print(f"Process exited with code {returncode}")
            return returncode
        
        print("=" * 80)
        print("Auto process completed successfully!")
        print("=" * 80)
        
        return 0
    
    except Exception as e:
        print(f"Error running setup_environment.py: {e}")
        return 1

if __name__ == "__main__":
    # By default, run with no timeout
    sys.exit(main(timeout=None))
