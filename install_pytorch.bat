@echo off
echo Installing PyTorch with CUDA support...

:: Check if pip is available
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python pip not found. Please install Python first.
    exit /b 1
)

:: Install PyTorch with CUDA 11.8 support
echo Installing PyTorch, torchvision, and torchaudio with CUDA 11.8...
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

if %errorlevel% neq 0 (
    echo PyTorch installation failed.
    exit /b 1
)

echo PyTorch with CUDA support installed successfully!
exit /b 0