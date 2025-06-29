@echo off
echo Setting up dependencies for Book Processor...
echo.

REM Add Tesseract to PATH if it exists
echo Checking for Tesseract...
IF EXIST "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo Found Tesseract at C:\Program Files\Tesseract-OCR
    SET "PATH=C:\Program Files\Tesseract-OCR;%PATH%"
    echo Added Tesseract to PATH
) ELSE (
    echo Tesseract not found at C:\Program Files\Tesseract-OCR
    echo Please install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
)

echo Checking for DjVuLibre...
IF EXIST "C:\Program Files\DjVuLibre\ddjvu.exe" (
    echo Found DjVuLibre at C:\Program Files\DjVuLibre
    SET "PATH=C:\Program Files\DjVuLibre;%PATH%"
    echo Added DjVuLibre to PATH
) ELSE (
    echo DjVuLibre not found at C:\Program Files\DjVuLibre
    echo Please install DjVuLibre from https://sourceforge.net/projects/djvu/
)


REM Verify dependencies are in PATH
echo.
echo Verifying dependencies...
where tesseract 2>NUL
IF %ERRORLEVEL% EQU 0 (
    echo Tesseract is available:
    tesseract --version
) ELSE (
    echo Tesseract is not available in PATH
)

where ddjvu 2>NUL
IF %ERRORLEVEL% EQU 0 (
    echo ddjvu is available:
    ddjvu --version
) ELSE (
    echo ddjvu is not available in PATH
)


echo.
echo Setup complete!
echo You can now run the book processor with: python process_book.py
echo.
pause
