#!/usr/bin/env python3
"""
Monitor Files Script - Count files in a directory every few seconds
"""
import os
import sys
import time
from datetime import datetime

def count_files(directory):
    """Count files in a directory"""
    try:
        return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Default directory path
    base_path = r"C:\Users\dglas\Dropbox\Books\2012 RTE Manual"
    
    # Check if command line argument is provided
    if len(sys.argv) > 1:
        try:
            # Check if the argument is a string of digits only
            if sys.argv[1].isdigit():
                # Construct the base path with the provided number
                book_dir = base_path + f" ({sys.argv[1]})"
            else:
                print("Error: Argument must be a number.")
                sys.exit(1)
        except Exception as e:
            print(f"Error processing argument: {str(e)}")
            sys.exit(1)
    else:
        # Use default path without number
        book_dir = base_path
    
    # Define paths for both directories
    images_dir = os.path.join(book_dir, "images")
    text_dir = os.path.join(book_dir, "text")
    
    # Interval in seconds
    interval = 5
    
    print(f"Monitoring files in:\n- {images_dir}\n- {text_dir}")
    print(f"Updating every {interval} seconds. Press Ctrl+C to stop.")
    print("-" * 70)
    
    try:
        while True:
            # Get current time
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Count files in both directories
            images_count = count_files(images_dir)
            text_count = count_files(text_dir)
            
            # Display the counts with full paths
            print(f"{current_time}:")
            print(f"  {images_dir}: {images_count}")
            print(f"  {text_dir}: {text_count}")
            print("-" * 70)
            
            # Wait for the specified interval
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
