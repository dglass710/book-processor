#!/usr/bin/env python3
"""
Monitor Files Script - Count files in a directory every few seconds
"""
import os
import time
from datetime import datetime

def count_files(directory):
    """Count files in a directory"""
    try:
        return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Directory to monitor
    directory = r"C:\Users\dglas\Dropbox\Books\2012 RTE Manual (4)\images"
    
    # Interval in seconds
    interval = 5
    
    print(f"Monitoring files in: {directory}")
    print(f"Updating every {interval} seconds. Press Ctrl+C to stop.")
    print("-" * 50)
    
    try:
        while True:
            # Get current time
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Count files
            file_count = count_files(directory)
            
            # Display the count
            print(f"{current_time} - Files: {file_count}")
            
            # Wait for the specified interval
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
