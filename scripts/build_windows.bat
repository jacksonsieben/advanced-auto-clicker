@echo off
setlocal

REM Check if version argument is provided
if "%~1"=="" (
    echo Usage: build_windows.bat ^<version^>
    exit /b 1
)

set VERSION=%~1

echo Checking dependencies for Advanced Auto Clicker...
call install_deps.bat

echo Building Advanced Auto Clicker for Windows, version %VERSION%...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    echo Please run install_deps.bat first
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller is not installed!
    echo Please run install_deps.bat first
    pause
    exit /b 1
)

REM Run the build script, pass the version as an argument
echo Running build script...
python build_exe.py %VERSION%

REM Check if build was successful
if exist "dist\AdvancedAutoClicker_v%VERSION%.exe" (
    echo.
    echo Build completed successfully!
    echo Executable created: dist\AdvancedAutoClicker_v%VERSION%.exe
    echo.
    echo You can now distribute the executable file.
    echo Configuration files will be stored in a "configs" folder next to the executable.
) else (
    echo.
    echo Build failed! Please check the error messages above.
)

pause
endlocal
