@echo off
echo Installing dependencies for Advanced Auto Clicker...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Installing required packages...
pip install -r requirements.txt

REM Install PyInstaller for building executable
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Dependencies installed successfully!
echo You can now build the executable by running: python build_exe.py
pause
