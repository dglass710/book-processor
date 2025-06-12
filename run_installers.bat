@echo off
echo Running installers for Book Processor dependencies...
echo.
echo This will open the installer programs. Please follow the installation prompts.
echo Make sure to select the option to add the programs to your PATH during installation.
echo.
pause

echo Running Tesseract installer...
start "" "c:\Users\dglas\Dropbox\Books\George F. Van Patten, aka Jorge Cervantes - The Cannabis Encyclopedia-Van Patten Publishing, USA (2015)\book_processor\dependencies\tesseract-installer.exe"
echo Please complete the Tesseract installation before continuing.
pause

echo Running DjVuLibre installer...
start "" "c:\Users\dglas\Dropbox\Books\George F. Van Patten, aka Jorge Cervantes - The Cannabis Encyclopedia-Van Patten Publishing, USA (2015)\book_processor\dependencies\djvulibre-installer.exe"
echo Please complete the DjVuLibre installation before continuing.
pause


echo.
echo Installation complete!
echo Please restart your command prompt to ensure PATH is updated.
pause
