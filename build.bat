@echo off
echo ========================================
echo    SRT Maker Build Script
echo ========================================

:: Check if PyInstaller is installed
echo Checking PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

:: Create cache directory if it doesn't exist
if not exist "cache" mkdir cache

:: Check PyInstaller path
set "PYINSTALLER_CMD="
where pyinstaller >nul 2>&1
if %errorlevel% equ 0 (
    set "PYINSTALLER_CMD=pyinstaller"
) else (
    set "PYINSTALLER_CMD=python -m PyInstaller"
)

:: Build the executable
echo Building SRT Maker executable...
%PYINSTALLER_CMD% --onefile --windowed --name "SRT_Maker" --icon=icon.ico --add-data "cache;cache" --hidden-import=torch --hidden-import=transformers --hidden-import=matplotlib --hidden-import=matplotlib.pyplot --hidden-import=matplotlib.backends --hidden-import=matplotlib.backends.backend_qt5agg --hidden-import=matplotlib.figure --hidden-import=deep_translator --hidden-import=deep_translator.constants --hidden-import=pysrt --hidden-import=ass --hidden-import=PyQt5 --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtWidgets --hidden-import=PyQt5.QtGui --hidden-import=sqlite3 --hidden-import=requests --collect-all matplotlib main.py

if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

:: Copy additional files to dist folder
echo Copying additional files...
if exist "dist\SRT_Maker.exe" (
    copy "requirements.txt" "dist\" >nul 2>&1
    copy "README.md" "dist\" >nul 2>&1
    if exist "icon.ico" copy "icon.ico" "dist\" >nul 2>&1
    if not exist "dist\cache" mkdir "dist\cache"
    if exist "cache\*.json" copy "cache\*.json" "dist\cache\" >nul 2>&1
)

echo ========================================
echo    Build completed successfully!
echo ========================================
echo Executable created: dist\SRT_Maker.exe
echo File size: 
for %%A in ("dist\SRT_Maker.exe") do echo %%~zA bytes
pause