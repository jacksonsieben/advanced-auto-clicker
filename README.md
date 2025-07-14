# Advanced Auto Clicker

A modern and feature-rich auto clicker application with global hotkeys, precise timing control, and advanced features.

## Features

- **Global Hotkeys**: Work even when the window is not focused
- **Precise Timing**: Control intervals down to milliseconds
- **Location Picking**: Click at specific coordinates or current cursor position
- **Mouse Movement Detection**: Pause clicking when mouse moves (optional)
- **Configuration Management**: Save and load different configurations
- **Portable**: No installation required, works from any directory
- **Cross-Platform**: Supports both Windows and Linux

## Building Executable

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Windows

1. Install dependencies:
   ```cmd
   install_deps.bat
   ```

2. Build executable:
   ```cmd
   python build_exe.py
   ```

3. The executable will be created in the `dist` folder as `AdvancedAutoClicker.exe`

### Linux

1. Make scripts executable:
   ```bash
   chmod +x install_deps.sh build_linux.sh
   ```

2. Install dependencies:
   ```bash
   ./install_deps.sh
   ```

3. Build executable:
   ```bash
   ./build_linux.sh
   ```

4. The executable will be created in the `dist` folder as `AdvancedAutoClicker`

## Running the Application

### From Source
```bash
python src/main.py
```

### From Executable
- **Windows**: Double-click `AdvancedAutoClicker.exe`
- **Linux**: Run `./AdvancedAutoClicker` from terminal

## Portable Usage

The application is designed to be fully portable:

- Configuration files are stored in a `configs` folder next to the executable
- No registry entries or system files are modified
- Can be run from USB drives or any directory
- Automatically saves last configuration on exit

## Configuration Files

- Configurations are saved as JSON files
- Default configuration is auto-saved as `configs/last_config.json`
- You can save/load multiple configuration profiles
- Configuration files can be shared between different installations

## Safety Features

- **Emergency Stop**: Move mouse to top-left corner to immediately stop clicking
- **Global Hotkeys**: Default F6 (start/stop) and F7 (stop only)
- **Mouse Movement Detection**: Optional feature to pause when mouse moves
- **Fail-Safe**: Built-in PyAutoGUI fail-safe protection

## Default Hotkeys

- **F6**: Start/Stop clicking (toggle)
- **F7**: Stop clicking only
- **ESC**: Cancel location picking mode

Hotkeys are fully customizable through the application interface.

## Troubleshooting

### Windows
- If you get DLL errors, install Microsoft Visual C++ Redistributable
- Run as administrator if you encounter permission issues
- Antivirus might flag the executable as suspicious (false positive)

### Linux
- Install required system packages: `sudo apt install python3-tk python3-dev`
- For global hotkeys to work, you might need to run with appropriate permissions
- Some Linux distributions require additional X11 libraries

## File Structure

```
AdvancedAutoClicker/
├── src/
│   └── main.py                 # Main application source
├── configs/                    # Configuration files (created automatically)
│   └── last_config.json       # Auto-saved configuration
├── dist/                       # Built executables (after building)
├── requirements.txt            # Python dependencies
├── build_exe.py               # Windows build script
├── build_linux.sh             # Linux build script
├── install_deps.bat            # Windows dependency installer
├── install_deps.sh             # Linux dependency installer
└── README.md                   # This file
```

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
