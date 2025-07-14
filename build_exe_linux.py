import PyInstaller.__main__
import sys
import os

def build_executable():
    """Build the auto clicker as an executable for Linux"""
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, "src")
    main_file = os.path.join(src_dir, "main.py")
    
    # PyInstaller arguments for Linux
    args = [
        main_file,
        '--onefile',  # Create a single executable file
        '--windowed',  # Don't show console window
        '--name=AdvancedAutoClicker',
        '--add-data=src:src',  # Include src directory (Linux uses : instead of ;)
        '--hidden-import=customtkinter',
        '--hidden-import=pyautogui',
        '--hidden-import=keyboard',
        '--hidden-import=pynput',
        '--hidden-import=PIL',
        '--hidden-import=tkinter',
        '--clean',  # Clean cache and remove temporary files
        '--noconfirm',  # Replace output directory without asking
        f'--distpath={os.path.join(current_dir, "dist")}',
        f'--workpath={os.path.join(current_dir, "build")}',
        f'--specpath={current_dir}',
    ]
    
    # Remove any empty arguments
    args = [arg for arg in args if arg.strip()]
    
    print("Building executable for Linux...")
    print(f"Main file: {main_file}")
    print(f"Arguments: {' '.join(args)}")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("Build completed!")
    print(f"Executable created in: {os.path.join(current_dir, 'dist')}")

if __name__ == "__main__":
    build_executable()
