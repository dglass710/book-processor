# PowerShell script to process a book with predefined responses
Write-Host "================================================================================"
Write-Host "Running Book Processor with Predefined Responses"
Write-Host "================================================================================"

# Set environment variable for the input file
$env:BOOK_PROCESSOR_INPUT_FILE = "C:\Users\dglas\Dropbox\Books\2012 RTE Manual.pdf"

# Get the content of the responses file
$responses = Get-Content -Path ".\rte_manual_responses.txt" -Raw

# Run the Python script with the responses as input
$responses | python setup_environment.py

Write-Host "================================================================================"
Write-Host "Process completed"
Write-Host "================================================================================"

# Wait for user input before closing
Read-Host -Prompt "Press Enter to exit"
