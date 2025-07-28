@echo off
echo ========================================
echo    SRT Maker Advanced Build Script
echo ========================================

:: Install build dependencies
echo Installing build dependencies...
python -m pip install pyinstaller auto-py-to-exe

:: Check PyInstaller path
set "PYINSTALLER_PATH="
where pyinstaller >nul 2>&1
if %errorlevel% equ 0 (
    set "PYINSTALLER_PATH=pyinstaller"
) else (
    set "PYINSTALLER_PATH=python -m PyInstaller"
)

:: Build using existing spec file
echo Building with advanced configuration...
if exist "SRT_Maker.spec" (
    %PYINSTALLER_PATH% SRT_Maker.spec --clean --noconfirm
) else (
    %PYINSTALLER_PATH% --onefile --windowed --name "SRT_Maker" --icon=icon.ico --add-data "cache;cache" --hidden-import=torch --hidden-import=transformers --hidden-import=matplotlib --hidden-import=deep_translator --hidden-import=pysrt --hidden-import=ass main.py
)

if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

:: Create portable package
echo Creating portable package...
if exist "dist\SRT_Maker.exe" (
    if not exist "SRT_Maker_Portable" mkdir "SRT_Maker_Portable"
    copy "dist\SRT_Maker.exe" "SRT_Maker_Portable\" >nul
    copy "README.md" "SRT_Maker_Portable\" >nul 2>&1
    copy "requirements.txt" "SRT_Maker_Portable\" >nul 2>&1
    if not exist "SRT_Maker_Portable\cache" mkdir "SRT_Maker_Portable\cache"
    
    :: Create launcher script
    echo @echo off > "SRT_Maker_Portable\Launch_SRT_Maker.bat"
    echo cd /d "%%~dp0" >> "SRT_Maker_Portable\Launch_SRT_Maker.bat"
    echo SRT_Maker.exe >> "SRT_Maker_Portable\Launch_SRT_Maker.bat"
    echo pause >> "SRT_Maker_Portable\Launch_SRT_Maker.bat"
)

:: Clean up build files
echo Cleaning up...
if exist "build" rmdir /s /q "build"
if exist "SRT_Maker.spec" del "SRT_Maker.spec"

echo ========================================
echo    Advanced build completed!
echo ========================================
echo Executable: dist\SRT_Maker.exe
echo Portable package: SRT_Maker_Portable\
if exist "dist\SRT_Maker.exe" (
    for %%A in ("dist\SRT_Maker.exe") do echo File size: %%~zA bytes
)
pause