#!/bin/bash

# Linux build script for Advanced Auto Clicker

echo "Building Advanced Auto Clicker for Linux..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Get current directory
CURRENT_DIR=$(dirname $(readlink -f $0))
SRC_DIR="$CURRENT_DIR/src"
MAIN_FILE="$SRC_DIR/main.py"

# Build executable
pyinstaller "$MAIN_FILE" \
    --onefile \
    --windowed \
    --name="AdvancedAutoClicker" \
    --add-data="src:src" \
    --hidden-import=customtkinter \
    --hidden-import=pyautogui \
    --hidden-import=keyboard \
    --hidden-import=pynput \
    --hidden-import=PIL \
    --hidden-import=tkinter \
    --clean \
    --noconfirm \
    --distpath="$CURRENT_DIR/dist" \
    --workpath="$CURRENT_DIR/build" \
    --specpath="$CURRENT_DIR"

echo "Build completed!"
echo "Executable created in: $CURRENT_DIR/dist"

# Make executable... executable
chmod +x "$CURRENT_DIR/dist/AdvancedAutoClicker"

echo "Done! You can run the executable with: ./dist/AdvancedAutoClicker"
