@echo off
echo ========================================
echo    SRT Maker Setup Script
echo ========================================

:: Check if any Python version is installed
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python 3.11.5...
    goto :install_python
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo Python is already installed. Proceeding with requirements installation...
goto :install_requirements

:install_python
echo Downloading Python 3.11.5...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe' -OutFile 'python-3.11.5-installer.exe'"

if not exist "python-3.11.5-installer.exe" (
    echo Failed to download Python installer.
    pause
    exit /b 1
)

echo Installing Python 3.11.5...
python-3.11.5-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: Wait for installation to complete
timeout /t 15 /nobreak >nul

:: Clean up installer
del python-3.11.5-installer.exe

:: Add Python to PATH manually if not already there
echo Adding Python to system PATH...
setx PATH "%PATH%;C:\Python313;C:\Python313\Scripts" /M >nul 2>&1
set PATH=%PATH%;C:\Python313;C:\Python313\Scripts

:: Refresh environment variables
for /f "skip=2 tokens=3*" %%a in ('reg query HKLM\SYSTEM\CurrentControlSet\Control\Session" Manager\Environment" /v PATH') do set PATH=%%b

echo Python 3.11.5 installation completed and added to PATH.

:install_requirements
echo Installing requirements from requirements.txt...

if not exist "requirements.txt" (
    echo requirements.txt not found in current directory.
    pause
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

if %errorlevel% neq 0 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo ========================================
echo    Setup completed successfully!
echo ========================================
echo You can now run: python main.py
pause