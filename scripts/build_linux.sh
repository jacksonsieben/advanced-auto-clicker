#!/bin/bash

# Linux build script for Advanced Auto Clicker

VERSION="$1"

if [ -z "$VERSION" ]; then
  echo "No version supplied. Usage: ./build-linux.sh <version>"
  exit 1
fi

echo "Building Advanced Auto Clicker for Linux, version $VERSION..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Get current directory and project root
CURRENT_DIR=$(dirname $(readlink -f $0))
PROJECT_ROOT="$(dirname "$CURRENT_DIR")"
SRC_DIR="$PROJECT_ROOT/src"
MAIN_FILE="$SRC_DIR/main.py"

# Build executable with versioned name
pyinstaller "$MAIN_FILE" \
    --onefile \
    --windowed \
    --name="AdvancedAutoClicker_v$VERSION" \
    --add-data="$SRC_DIR:src" \
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

# Make executable executable
chmod +x "$CURRENT_DIR/dist/AdvancedAutoClicker_v$VERSION"

echo "Done! You can run the executable with: ./dist/AdvancedAutoClicker_v$VERSION"
