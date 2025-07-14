import PyInstaller.__main__
import sys
import os

def create_icon():
    """Try to create an icon for the application"""
    try:
        import scripts.create_icon as create_icon
        return create_icon.create_icon()
    except Exception as e:
        print(f"Could not create icon: {e}")
        return None

def build_executable():
    """Build the auto clicker as an executable"""

    # Get version from command line, default to "0.0.0"
    version = sys.argv[1] if len(sys.argv) > 1 else "0.0.0"

    # Sanitize version string for filenames (optional)
    version_sanitized = version.replace(" ", "_").replace("/", "-")

    # Get the current directory and project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    src_dir = os.path.join(project_root, "src")
    main_file = os.path.join(src_dir, "main.py")

    # Try to create icon
    icon_path = create_icon()

    exe_name = f"AdvancedAutoClicker_v{version_sanitized}"

    # PyInstaller arguments
    args = [
        main_file,
        '--onefile',  # Create a single executable file
        '--windowed',  # Don't show console window (Windows)
        f'--name={exe_name}',
        f'--add-data={src_dir};src',  # Include src directory
        '--hidden-import=customtkinter',
        '--hidden-import=pyautogui',
        '--hidden-import=keyboard',
        '--hidden-import=pynput',
        '--hidden-import=pynput.keyboard',
        '--hidden-import=pynput.mouse',
        '--hidden-import=PIL',
        '--hidden-import=tkinter',
        '--clean',  # Clean cache and remove temporary files
        '--noconfirm',  # Replace output directory without asking
        f'--distpath={os.path.join(current_dir, "dist")}',
        f'--workpath={os.path.join(current_dir, "build")}',
        f'--specpath={current_dir}',
    ]

    # Add icon if it exists
    if icon_path and os.path.exists(icon_path):
        args.append(f'--icon={icon_path}')

    # Remove any empty arguments
    args = [arg for arg in args if arg.strip()]

    print("Building executable...")
    print(f"Main file: {main_file}")
    print(f"Version: {version}")
    print(f"Arguments: {' '.join(args)}")

    # Run PyInstaller
    PyInstaller.__main__.run(args)

    print("Build completed!")
    print(f"Executable created in: {os.path.join(current_dir, 'dist')}")

if __name__ == "__main__":
    build_executable()
