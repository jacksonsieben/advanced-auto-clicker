import customtkinter as ctk
from tkinter import messagebox
import pyautogui
import threading
import time
import keyboard
from pynput import mouse, keyboard as pynput_keyboard
from customtkinter import ThemeManager
import json
import os
import sys
from tkinter import filedialog


# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

FG_COLOR = ThemeManager.theme["CTkFrame"]["fg_color"]

def get_executable_directory():
    """Get the directory where the executable is located"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def get_config_directory():
    """Get the directory for storing configuration files"""
    exe_dir = get_executable_directory()
    config_dir = os.path.join(exe_dir, "configs")
    
    # Create config directory if it doesn't exist
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
        except Exception as e:
            print(f"Warning: Could not create config directory: {e}")
            # Fallback to executable directory
            return exe_dir
    
    return config_dir

class ModernAutoClickerApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🖱️ Advanced Auto Clicker")
        self.root.geometry("580x880")  # Reduced height for more compact layout
        self.root.resizable(False, False)
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.001  # Reduced pause for better performance
        
        # Variables
        self.clicking = False
        self.click_thread = None
        self.click_count = 0
        self.total_clicks = 0
        self.picking_location = False
        self.mouse_listener = None

        self.currently_recording = None
        self.pressed_keys = set()
        self.hotkey_start = "f6"
        self.hotkey_stop = "f7"
        
        # Mouse movement detection
        self.idle_mode_enabled = False
        self.mouse_movement_listener = None
        self.keyboard_listener = None
        self.last_mouse_position = None
        self.last_activity_time = 0
        self.idle_delay = 1.0  # seconds after activity stops to resume clicking

        self.create_widgets()
        self.setup_global_hotkeys()
        
        # Auto-load last configuration
        self.auto_load_configuration()
        
    def create_widgets(self):
        # Create menu first
        self.create_menu()
        
        # Main container with padding
        main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Click Interval Frame
        interval_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        interval_frame.pack(fill="x", padx=20, pady=15)
        
        interval_title = ctk.CTkLabel(
            interval_frame,
            text="⏱️ Click Interval",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        interval_title.pack(pady=(15, 10))
        
        # Time inputs in a grid
        time_frame = ctk.CTkFrame(interval_frame, fg_color="transparent")
        time_frame.pack(pady=(0, 15))
        
        # Hours
        hours_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        hours_frame.grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkLabel(hours_frame, text="Hours:", font=ctk.CTkFont(size=12)).pack()
        self.hours_var = ctk.StringVar(value="0")
        self.hours_entry = ctk.CTkEntry(hours_frame, width=60, textvariable=self.hours_var, justify="center")
        self.hours_entry.pack(pady=(5, 0))
        
        # Minutes
        minutes_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        minutes_frame.grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(minutes_frame, text="Minutes:", font=ctk.CTkFont(size=12)).pack()
        self.minutes_var = ctk.StringVar(value="0")
        self.minutes_entry = ctk.CTkEntry(minutes_frame, width=60, textvariable=self.minutes_var, justify="center")
        self.minutes_entry.pack(pady=(5, 0))
        
        # Seconds
        seconds_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        seconds_frame.grid(row=0, column=2, padx=10, pady=5)
        ctk.CTkLabel(seconds_frame, text="Seconds:", font=ctk.CTkFont(size=12)).pack()
        self.seconds_var = ctk.StringVar(value="1")
        self.seconds_entry = ctk.CTkEntry(seconds_frame, width=60, textvariable=self.seconds_var, justify="center")
        self.seconds_entry.pack(pady=(5, 0))
        
        # Milliseconds
        ms_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        ms_frame.grid(row=0, column=3, padx=10, pady=5)
        ctk.CTkLabel(ms_frame, text="Milliseconds:", font=ctk.CTkFont(size=12)).pack()
        self.milliseconds_var = ctk.StringVar(value="0")
        self.milliseconds_entry = ctk.CTkEntry(ms_frame, width=80, textvariable=self.milliseconds_var, justify="center")
        self.milliseconds_entry.pack(pady=(5, 0))
        
        # Container for Mouse Button and Click Repeat frames (side by side)
        button_repeat_container = ctk.CTkFrame(main_frame, fg_color=FG_COLOR)
        button_repeat_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # Mouse Button Frame
        button_frame = ctk.CTkFrame(button_repeat_container, corner_radius=10)
        button_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        button_title = ctk.CTkLabel(
            button_frame,
            text="🖱️ Mouse Button",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        button_title.pack(pady=(15, 10))
        
        button_options_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_options_frame.pack(pady=(0, 15))
        
        self.button_var = ctk.StringVar(value="left")
        self.left_radio = ctk.CTkRadioButton(button_options_frame, text="Left", variable=self.button_var, value="left")
        self.left_radio.pack(pady=2)
        self.right_radio = ctk.CTkRadioButton(button_options_frame, text="Right", variable=self.button_var, value="right")
        self.right_radio.pack(pady=2)
        self.middle_radio = ctk.CTkRadioButton(button_options_frame, text="Middle", variable=self.button_var, value="middle")
        self.middle_radio.pack(pady=2)
        
        # Click Repeat Frame
        repeat_frame = ctk.CTkFrame(button_repeat_container, corner_radius=10)
        repeat_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        repeat_title = ctk.CTkLabel(
            repeat_frame,
            text="🔄 Click Repeat",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        repeat_title.pack(pady=(15, 10))
        
        repeat_options_frame = ctk.CTkFrame(repeat_frame, fg_color="transparent")
        repeat_options_frame.pack(pady=(0, 15))
        
        self.repeat_var = ctk.StringVar(value="forever")
        self.forever_radio = ctk.CTkRadioButton(repeat_options_frame, text="Forever", variable=self.repeat_var, value="forever", command=self.on_repeat_change)
        self.forever_radio.pack(pady=2)
        
        times_frame = ctk.CTkFrame(repeat_options_frame, fg_color="transparent")
        times_frame.pack(pady=2)
        
        self.times_radio = ctk.CTkRadioButton(times_frame, text="Times:", variable=self.repeat_var, value="times", command=self.on_repeat_change)
        self.times_radio.pack(side="left")
        
        self.times_var = ctk.StringVar(value="100")
        self.times_entry = ctk.CTkEntry(times_frame, width=80, textvariable=self.times_var, justify="center")
        self.times_entry.pack(side="left", padx=(10, 0))
        self.times_entry.configure(state="disabled")
        
        # Click Location Frame
        location_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        location_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        location_title = ctk.CTkLabel(
            location_frame,
            text="📍 Click Location",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        location_title.pack(pady=(15, 10))
        
        # Location options
        self.location_var = ctk.StringVar(value="current")
        self.current_radio = ctk.CTkRadioButton(
            location_frame, 
            text="Current cursor location", 
            variable=self.location_var, 
            value="current", 
            command=self.on_location_change
        )
        self.current_radio.pack(pady=5)
        
        self.pick_radio = ctk.CTkRadioButton(
            location_frame, 
            text="Pick location (click anywhere on screen):", 
            variable=self.location_var, 
            value="pick", 
            command=self.on_location_change
        )
        self.pick_radio.pack(pady=5)
        
        # Container for coordinates and button
        pick_container = ctk.CTkFrame(location_frame, fg_color="transparent")
        pick_container.pack(fill="x", pady=(10, 15))
        
        # X, Y coordinates and button in the same row
        coords_frame = ctk.CTkFrame(pick_container, fg_color="transparent")
        coords_frame.pack()
        
        x_frame = ctk.CTkFrame(coords_frame, fg_color="transparent")
        x_frame.pack(side="left", padx=15)
        ctk.CTkLabel(x_frame, text="X:", font=ctk.CTkFont(size=12)).pack()
        self.x_var = ctk.StringVar(value="0")
        self.x_entry = ctk.CTkEntry(x_frame, width=80, textvariable=self.x_var, justify="center")
        self.x_entry.pack(pady=(5, 0))
        self.x_entry.configure(state="disabled")
        
        y_frame = ctk.CTkFrame(coords_frame, fg_color="transparent")
        y_frame.pack(side="left", padx=15)
        ctk.CTkLabel(y_frame, text="Y:", font=ctk.CTkFont(size=12)).pack()
        self.y_var = ctk.StringVar(value="0")
        self.y_entry = ctk.CTkEntry(y_frame, width=80, textvariable=self.y_var, justify="center")
        self.y_entry.pack(pady=(5, 0))
        self.y_entry.configure(state="disabled")
        
        # Pick location button on the same row
        button_frame = ctk.CTkFrame(coords_frame, fg_color="transparent")
        button_frame.pack(side="left", padx=15)
        ctk.CTkLabel(button_frame, text=" ", font=ctk.CTkFont(size=12)).pack()  # Spacer for alignment
        self.get_pos_btn = ctk.CTkButton(
            button_frame,
            text="🎯 Pick Location",
            command=self.pick_location,
            height=32,
            width=120,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.get_pos_btn.pack(pady=(5, 0))
        self.get_pos_btn.configure(state="disabled")
        
        # Idle Mode Detection Frame
        idle_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        idle_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        idle_title = ctk.CTkLabel(
            idle_frame,
            text="💤 Idle Mode Detection",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        idle_title.pack(pady=(15, 10))
        
        # Idle detection option
        idle_options_frame = ctk.CTkFrame(idle_frame, fg_color="transparent")
        idle_options_frame.pack(pady=(0, 10))
        
        self.idle_detection_var = ctk.BooleanVar(value=False)
        self.idle_checkbox = ctk.CTkCheckBox(
            idle_options_frame,
            text="Only click when user is idle (no mouse/keyboard activity)",
            variable=self.idle_detection_var,
            command=self.on_idle_detection_change,
            font=ctk.CTkFont(size=12)
        )
        self.idle_checkbox.pack(pady=5)
        
        # Idle delay setting
        delay_frame = ctk.CTkFrame(idle_options_frame, fg_color="transparent")
        delay_frame.pack(pady=(5, 0))
        
        ctk.CTkLabel(
            delay_frame,
            text="Resume delay after activity stops (seconds):",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=(0, 10))
        
        self.idle_delay_var = ctk.StringVar(value="1.0")
        self.idle_delay_entry = ctk.CTkEntry(
            delay_frame,
            width=60,
            textvariable=self.idle_delay_var,
            justify="center",
            font=ctk.CTkFont(size=11)
        )
        self.idle_delay_entry.pack(side="left")
        
        # Performance tip
        performance_tip = ctk.CTkLabel(
            idle_options_frame,
            text="💡 Tip: Disable idle mode if you experience mouse lag",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        performance_tip.pack()
        
        # Idle status indicator
        self.idle_status_label = ctk.CTkLabel(
            idle_frame,
            text="🔘 Idle mode disabled",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.idle_status_label.pack()
        
        self.enable_status_frame = False

        # StatusFrame
        if self.enable_status_frame:
            status_frame = ctk.CTkFrame(main_frame, corner_radius=10)
            status_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            status_title = ctk.CTkLabel(
                status_frame,
                text="📊 Status",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            status_title.pack(pady=(15, 10))
            
            self.status_label = ctk.CTkLabel(
                status_frame,
                text="🟢 Ready",
                font=ctk.CTkFont(size=14),
                wraplength=500  # Allow text wrapping
            )
            self.status_label.pack(pady=10, padx=10)
            
            self.clicks_label = ctk.CTkLabel(
                status_frame,
                text="Clicks: 0",
                font=ctk.CTkFont(size=14)
            )
            self.clicks_label.pack(pady=(0, 15))
        
        # Control Buttons
        control_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        control_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.start_btn = ctk.CTkButton(
            control_frame,
            text=f"▶️ Start ({self.hotkey_start.upper()})",
            command=self.start_clicking,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        self.stop_btn = ctk.CTkButton(
            control_frame,
            text=f"⏹️ Stop ({self.hotkey_stop.upper()})",
            command=self.stop_clicking,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        self.stop_btn.pack(side="left", fill="x", expand=True)
        self.stop_btn.configure(state="disabled")
        
    def create_help_window(self):
        """Create and show the help/instructions window"""
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("📖 Instructions")
        help_window.geometry("500x400")
        help_window.resizable(False, False)
        
        # Make window modal
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Center the window
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (help_window.winfo_screenheight() // 2) - (400 // 2)
        help_window.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(help_window, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="📖 Instructions",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 20))
        
        # Instructions text
        instructions_text = f"""🔥 Global Hotkeys (work even when window is not focused):
• {self.hotkey_start.upper()}: Start/Stop clicking
• {self.hotkey_stop.upper()}: Stop clicking
• Move mouse to top-left corner for emergency stop

💡 Tips:
• Use 'Pick Location' to click anywhere and set coordinates
• Make sure the target window is active before starting
• For very fast clicking, use milliseconds instead of seconds
• The app will automatically stop when max clicks is reached

� Idle Mode Detection:
• Enable to pause clicking when user is active (mouse or keyboard)
• Only clicks when user is completely idle (no movement/typing)
• Useful for preventing interruptions during work
• Configurable delay before resuming after activity stops
• Real-time status shows when clicks are paused

💾 Configuration Management:
• Save different configurations as JSON files
• Load saved configurations for different use cases
• Configurations are automatically saved when closing the app
• Share configurations with others or backup your settings

⚠️ Safety Features:
• Emergency stop by moving mouse to top-left corner
• Press ESC to cancel location picking
• Global hotkeys work even when window is minimized
• Idle mode detection prevents unwanted clicks during work

🎯 How to use:
1. Set your desired click interval
2. Choose mouse button (Left/Right/Middle)
3. Set repeat mode (Forever or specific number of times)
4. Choose click location (Current cursor or Pick specific location)
5. Optionally enable idle mode detection
6. Press Start or {self.hotkey_start.upper()} to begin clicking

🎮 Configure Hotkeys:
• Use the menu (☰) to access Hotkeys configuration
• Click on a hotkey field and press your desired key combination
• Both single keys (f6, f7) and combinations (ctrl+f6, alt+f7) are supported"""
        
        # Scrollable frame for instructions
        scrollable_frame = ctk.CTkScrollableFrame(main_frame, corner_radius=10)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        instructions_label = ctk.CTkLabel(
            scrollable_frame,
            text=instructions_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        instructions_label.pack(pady=10, padx=10)
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="✅ Close",
            command=help_window.destroy,
            height=35,
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        close_btn.pack(pady=(0, 20))
        
    def create_menu(self):
        """Create the hamburger menu"""
        menu_frame = ctk.CTkFrame(self.root, height=50, corner_radius=0, fg_color="transparent")
        menu_frame.pack(fill="x", pady=(0, 0))
        menu_frame.pack_propagate(False)
        
        # Menu button (hamburger style)
        menu_btn = ctk.CTkButton(
            menu_frame,
            text="☰",
            command=self.show_menu,
            width=40,
            height=30,
            corner_radius=5,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        menu_btn.pack(side="left", padx=10, pady=10)
        
        # Title in menu bar
        title_label = ctk.CTkLabel(
            menu_frame,
            text="🖱️ Advanced Auto Clicker",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=10)

        # Menu dropdown (initially hidden)
        self.menu_dropdown = None
        
    
    def menu_hotkeys_clicked(self):
        self.close_menu()
        self.create_hotkeys_window()
    
    def menu_configurations_clicked(self):
        """Handle configurations menu click"""
        self.close_menu()
        self.create_configurations_window()
        
    def create_hotkeys_window(self):
        hotkey_window = ctk.CTkToplevel(self.root)
        hotkey_window.title("🎮 Hotkeys Configuration")
        hotkey_window.geometry("450x550")
        hotkey_window.resizable(False, False)

        hotkey_window.transient(self.root)
        hotkey_window.grab_set()
        hotkey_window.focus_force()

        # Centralizar em relação à janela principal
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (450 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (550 // 2)
        hotkey_window.geometry(f"+{x}+{y}")

        # Main frame
        main_frame = ctk.CTkFrame(hotkey_window, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🎮 Hotkeys Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 10))

        # Instructions
        instructions_label = ctk.CTkLabel(
            main_frame,
            text="Click on the fields below and press the desired key combination",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        instructions_label.pack(pady=(0, 20))

        # Hotkeys frame
        hotkeys_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        hotkeys_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Start/Stop hotkey
        start_frame = ctk.CTkFrame(hotkeys_frame, fg_color="transparent")
        start_frame.pack(fill="x", padx=15, pady=15)

        start_label = ctk.CTkLabel(
            start_frame,
            text="🔄 Start/Stop Toggle:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        start_label.pack(anchor="w", pady=(0, 5))

        self.start_status_label = ctk.CTkLabel(
            start_frame,
            text=f"Current: {self.hotkey_start.upper()}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.start_status_label.pack(anchor="w", pady=(0, 5))

        self.start_hotkey_var = ctk.StringVar(value=self.hotkey_start)
        self.start_entry = ctk.CTkEntry(
            start_frame, 
            textvariable=self.start_hotkey_var, 
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.start_entry.pack(fill="x", pady=(0, 5))
        self.start_entry.bind("<Button-1>", lambda e: self.capture_hotkey_live(self.start_entry, "hotkey_start"))

        # Stop hotkey
        stop_frame = ctk.CTkFrame(hotkeys_frame, fg_color="transparent")
        stop_frame.pack(fill="x", padx=15, pady=(0, 15))

        stop_label = ctk.CTkLabel(
            stop_frame,
            text="⏹️ Stop Only:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        stop_label.pack(anchor="w", pady=(0, 5))

        self.stop_status_label = ctk.CTkLabel(
            stop_frame,
            text=f"Current: {self.hotkey_stop.upper()}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.stop_status_label.pack(anchor="w", pady=(0, 5))

        self.stop_hotkey_var = ctk.StringVar(value=self.hotkey_stop)
        self.stop_entry = ctk.CTkEntry(
            stop_frame, 
            textvariable=self.stop_hotkey_var, 
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.stop_entry.pack(fill="x", pady=(0, 5))
        self.stop_entry.bind("<Button-1>", lambda e: self.capture_hotkey_live(self.stop_entry, "hotkey_stop"))

        # Status indicator
        self.capture_status_label = ctk.CTkLabel(
            main_frame,
            text="💡 Click on a field above to capture a new hotkey",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.capture_status_label.pack(pady=(10, 15))

        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))

        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Cancel",
            command=hotkey_window.destroy,
            height=35,
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        def save():
            # Pega os valores atuais das variáveis
            start_hotkey = self.start_hotkey_var.get()
            stop_hotkey = self.stop_hotkey_var.get()
            
            if not start_hotkey or not stop_hotkey:
                messagebox.showerror("Error", "Both hotkeys must be defined")
                return
            if start_hotkey == stop_hotkey:
                messagebox.showerror("Error", "Start and Stop cannot be the same")
                return
            
            # Validate hotkeys by testing them
            try:
                keyboard.unhook_all()
                keyboard.add_hotkey(start_hotkey, lambda: None)
                keyboard.add_hotkey(stop_hotkey, lambda: None)
                keyboard.unhook_all()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid hotkey: {e}\n\nTry a different combination.")
                return
            
            # Salva nas variáveis globais
            self.hotkey_start = start_hotkey
            self.hotkey_stop = stop_hotkey
            
            print(f"Saving hotkeys: Start={self.hotkey_start}, Stop={self.hotkey_stop}")  # Debug
            
            # Re-registra as hotkeys globais
            self.setup_global_hotkeys()
            
            # Atualiza os textos dos botões
            self.update_button_texts()
            
            # Fecha a janela
            hotkey_window.destroy()
            
            # Mostra mensagem de sucesso
            messagebox.showinfo("Success", 
                              f"Hotkeys successfully updated!\n\n"
                              f"Start/Stop: {self.hotkey_start.upper()}\n"
                              f"Stop: {self.hotkey_stop.upper()}")

        save_btn = ctk.CTkButton(
            buttons_frame,
            text="✅ Save",
            command=save,
            height=35,
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_btn.pack(side="right", fill="x", expand=True, padx=(10, 0))

        # Store window reference for capture methods
        self.hotkey_window = hotkey_window


    def capture_hotkey_live(self, target_entry, target_attr):
        if self.currently_recording:
            return  # evita múltiplas capturas simultâneas

        self.currently_recording = target_attr
        captured_keys = set()

        # Visual feedback - change entry appearance
        target_entry.configure(
            placeholder_text="⏳ Press the keys...",
            fg_color=("red", "darkred"),
            border_color=("red", "red")
        )

        # Update status labels
        if target_attr == "hotkey_start":
            self.start_status_label.configure(text="🔴 RECORDING - Press the desired keys", text_color="red")
        else:
            self.stop_status_label.configure(text="🔴 RECORDING - Press the desired keys", text_color="red")

        # Update main status
        self.capture_status_label.configure(
            text="🔴 RECORDING: Press and hold the keys, then release all to save",
            text_color="red"
        )

        self.pressed_keys.clear()

        def on_press(event):
            key = event.name
            captured_keys.add(key)
            self.pressed_keys.add(key)

            # Converte teclas especiais para formato padrão
            display_keys = []
            for k in sorted(captured_keys):
                if k == "ctrl":
                    display_keys.append("ctrl")
                elif k == "alt":
                    display_keys.append("alt")
                elif k == "shift":
                    display_keys.append("shift")
                elif k == "cmd" or k == "windows":
                    display_keys.append("windows")
                else:
                    display_keys.append(k)

            combination = "+".join(display_keys)
            
            # Update the entry display with current combination
            target_entry.configure(state="normal")
            target_entry.delete(0, "end")
            target_entry.insert(0, combination.upper())
            target_entry.configure(state="readonly")

            # Update status to show current keys
            self.capture_status_label.configure(
                text=f"🔴 CURRENT: {combination.upper()} - Release all keys to save",
                text_color="orange"
            )

        def on_release(event):
            self.pressed_keys.discard(event.name)

            if not self.pressed_keys and captured_keys:
                # Cria a combinação final com formato correto
                final_keys = []
                for key in sorted(captured_keys):
                    if key == "ctrl":
                        final_keys.append("ctrl")
                    elif key == "alt":
                        final_keys.append("alt")
                    elif key == "shift":
                        final_keys.append("shift")
                    elif key == "cmd" or key == "windows":
                        final_keys.append("windows")
                    else:
                        final_keys.append(key)
                
                final_combo = "+".join(final_keys)
                setattr(self, target_attr, final_combo)
                
                # Atualiza a variável da interface
                if target_attr == "hotkey_start":
                    self.start_hotkey_var.set(final_combo)
                    self.start_status_label.configure(
                        text=f"✅ New: {final_combo.upper()}", 
                        text_color="green"
                    )
                elif target_attr == "hotkey_stop":
                    self.stop_hotkey_var.set(final_combo)
                    self.stop_status_label.configure(
                        text=f"✅ New: {final_combo.upper()}", 
                        text_color="green"
                    )
                
                # Reset entry appearance
                target_entry.configure(
                    fg_color=("gray90", "gray20"),
                    border_color=("gray70", "gray30")
                )
                
                # Update main status
                self.capture_status_label.configure(
                    text=f"✅ Captured: {final_combo.upper()}",
                    text_color="green"
                )
                
                print(f"Captured Hotkey: {target_attr} = {final_combo}")  # Debug
                
                self.currently_recording = None
                keyboard.unhook_all()

                # Reset status after 2 seconds
                def reset_status():
                    if hasattr(self, 'capture_status_label'):
                        self.capture_status_label.configure(
                            text="💡 Click on a field above to capture a new hotkey",
                            text_color="gray"
                        )
                    
                    if target_attr == "hotkey_start" and hasattr(self, 'start_status_label'):
                        self.start_status_label.configure(
                            text=f"Current: {final_combo.upper()}",
                            text_color="gray"
                        )
                    elif target_attr == "hotkey_stop" and hasattr(self, 'stop_status_label'):
                        self.stop_status_label.configure(
                            text=f"Current: {final_combo.upper()}",
                            text_color="gray"
                        )

                # Schedule reset after 2 seconds
                self.root.after(2000, reset_status)

        keyboard.unhook_all()
        keyboard.on_press(on_press)
        keyboard.on_release(on_release)


        
    def show_menu(self):
        """Show/hide the dropdown menu"""
        if self.menu_dropdown and self.menu_dropdown.winfo_exists():
            self.menu_dropdown.destroy()
            self.menu_dropdown = None
            return
        
        # Create dropdown menu
        self.menu_dropdown = ctk.CTkFrame(self.root, corner_radius=10)
        self.menu_dropdown.place(x=10, y=50)
        
        # Configurations button
        config_btn = ctk.CTkButton(
            self.menu_dropdown,
            text="💾 Configuration",
            command=self.menu_configurations_clicked,
            height=35,
            corner_radius=5,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        config_btn.pack(fill="x", padx=10, pady=10)
        
        # Hotkeys button
        hotkeys_btn = ctk.CTkButton(
            self.menu_dropdown,
            text="🎮 Hotkeys",
            command=self.menu_hotkeys_clicked,
            height=35,
            corner_radius=5,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        hotkeys_btn.pack(fill="x", padx=10, pady=(0, 10))

        # Help button
        help_btn = ctk.CTkButton(
            self.menu_dropdown,
            text="📖 Instructions",
            command=self.menu_help_clicked,
            height=35,
            corner_radius=5,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        help_btn.pack(fill="x", padx=10, pady=(0, 10))
        
        # About button
        about_btn = ctk.CTkButton(
            self.menu_dropdown,
            text="ℹ️ About",
            command=self.menu_about_clicked,
            height=35,
            corner_radius=5,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        about_btn.pack(fill="x", padx=10, pady=(0, 10))

        
        # Close menu when clicking outside
        self.root.bind("<Button-1>", self.close_menu)
        
    def close_menu(self, event=None):
        """Close the dropdown menu"""
        if self.menu_dropdown and self.menu_dropdown.winfo_exists():
            # Check if click was inside menu
            if event:
                menu_x = self.menu_dropdown.winfo_x()
                menu_y = self.menu_dropdown.winfo_y()
                menu_width = self.menu_dropdown.winfo_width()
                menu_height = self.menu_dropdown.winfo_height()
                
                click_x = event.x_root - self.root.winfo_x()
                click_y = event.y_root - self.root.winfo_y()
                
                if not (menu_x <= click_x <= menu_x + menu_width and 
                       menu_y <= click_y <= menu_y + menu_height):
                    self.menu_dropdown.destroy()
                    self.menu_dropdown = None
                    self.root.unbind("<Button-1>")
        
    def menu_help_clicked(self):
        """Handle help menu click"""
        self.close_menu()
        self.create_help_window()
        
    def menu_about_clicked(self):
        """Handle about menu click"""
        self.close_menu()
        messagebox.showinfo("About", 
                          "🖱️ Advanced Auto Clicker\n\n"
                          "A modern and feature-rich auto clicker application.\n\n"
                          "Features:\n"
                          "• Global hotkeys\n"
                          "• Precise timing control\n"
                          "• Location picking\n"
                          "• Safety features\n\n"
                          "Made with Python & CustomTkinter")
        
    def setup_global_hotkeys(self):
        """Setup global hotkeys that work even when the window is not in focus"""
        keyboard.unhook_all()
        try:
            print(f"Registering hotkeys: Start/Stop={self.hotkey_start}, Stop={self.hotkey_stop}")  # Debug
            
            # Validate hotkey format before registering
            if not self.hotkey_start or not self.hotkey_stop:
                raise ValueError("Hotkeys cannot be empty")
            
            # Try to register the hotkeys
            keyboard.add_hotkey(self.hotkey_start, self.toggle_clicking)
            keyboard.add_hotkey(self.hotkey_stop, self.stop_clicking)

            print(f"Hotkeys registered successfully!")  # Debug
        except Exception as e:
            print(f"Error registering hotkeys: {e}")

            # Reset to default hotkeys if there's an error
            self.hotkey_start = "f6"
            self.hotkey_stop = "f7"
            
            # Try to register default hotkeys
            try:
                keyboard.add_hotkey(self.hotkey_start, self.toggle_clicking)
                keyboard.add_hotkey(self.hotkey_stop, self.stop_clicking)
                print("Returning to default hotkeys: F6 and F7")

                # Update button texts with default hotkeys
                self.update_button_texts()
                
                messagebox.showwarning("Warning", 
                                     f"Error while registering the Hotkeys: {e}\n\n"
                                     "Returning to original hotkeys:\n"
                                     "F6 - Start/Stop\n"
                                     "F7 - Stop")
            except Exception as e2:
                print(f"Error registering default hotkeys: {e2}")
                messagebox.showerror("Error", 
                                   f"Critical error while registering hotkeys: {e2}\n\n"
                                   "Global hotkeys won't work.")
    
    
    def update_button_texts(self):
        """Update button texts to show current hotkeys"""
        if hasattr(self, 'start_btn') and hasattr(self, 'stop_btn'):
            start_key = self.hotkey_start.upper()
            stop_key = self.hotkey_stop.upper()

            print(f"Updating button texts: Start={start_key}, Stop={stop_key}")  # Debug

            if self.clicking:
                self.start_btn.configure(text=f"⏸️ Stop ({start_key})")
            else:
                self.start_btn.configure(text=f"▶️ Start ({start_key})")
            
            self.stop_btn.configure(text=f"⏹️ Stop ({stop_key})")

    
    def cleanup_hotkeys(self):
        """Cleanup global hotkeys when closing the application"""
        try:
            # Cancel location picking if active
            if self.picking_location:
                self.cancel_location_pick()
            
            # Stop idle mode monitoring
            self.stop_idle_monitoring()
            
            keyboard.unhook_all()
        except:
            pass
    
    def on_repeat_change(self):
        if self.repeat_var.get() == "times":
            self.times_entry.configure(state="normal")
        else:
            self.times_entry.configure(state="disabled")
    
    def on_location_change(self):
        if self.location_var.get() == "pick":
            self.x_entry.configure(state="normal")
            self.y_entry.configure(state="normal")
            self.get_pos_btn.configure(state="normal")
        else:
            self.x_entry.configure(state="disabled")
            self.y_entry.configure(state="disabled")
            self.get_pos_btn.configure(state="disabled")
    
    def get_current_position(self):
        # Give user 3 seconds to position mouse
        for i in range(3, 0, -1):
            self.status_label.configure(text=f"⏰ Position mouse cursor in {i} seconds...")
            self.root.update()
            time.sleep(1)
        
        x, y = pyautogui.position()
        self.x_var.set(str(x))
        self.y_var.set(str(y))
        self.status_label.configure(text=f"📍 Position captured: ({x}, {y})")
    
    def pick_location(self):
        """Start location picking mode"""
        if self.picking_location:
            return
        
        self.picking_location = True
        self.get_pos_btn.configure(text="⏳ Waiting...", state="disabled")
        
        if self.enable_status_frame:
            self.status_label.configure(text="🎯 Click anywhere on screen to define the position (ESC to cancel)")
        
        # Start mouse listener
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()
        
        # Setup ESC key listener in a separate thread
        def esc_listener():
            while self.picking_location:
                try:
                    if keyboard.is_pressed('esc'):
                        self.root.after(0, self.cancel_location_pick)
                        break
                    time.sleep(0.1)  # Check every 100ms
                except:
                    break
        
        threading.Thread(target=esc_listener, daemon=True).start()
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click during location picking"""
        if not self.picking_location:
            return
        
        # Only react to left mouse button press
        if pressed and button == mouse.Button.left:
            # Stop the mouse listener
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            
            # Set the location
            self.root.after(0, lambda: self.set_picked_location(int(x), int(y)))
    
    def set_picked_location(self, x, y):
        """Set the picked location coordinates"""
        self.picking_location = False
        self.x_var.set(str(x))
        self.y_var.set(str(y))
        self.get_pos_btn.configure(text="🎯 Pick Location", state="normal")
        
        if self.enable_status_frame:
            self.status_label.configure(text=f"✅ Defined position: ({x}, {y})")
    
    def cancel_location_pick(self):
        """Cancel location picking"""
        if not self.picking_location:
            return
        
        self.picking_location = False
        
        # Stop mouse listener
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        self.get_pos_btn.configure(text="🎯 Pick Location", state="normal")
        
        if self.enable_status_frame:
            self.status_label.configure(text="❌ Position selection cancelled")
    
    def get_interval(self):
        try:
            hours = int(self.hours_var.get() or 0)
            minutes = int(self.minutes_var.get() or 0)
            seconds = int(self.seconds_var.get() or 0)
            milliseconds = int(self.milliseconds_var.get() or 0)
            
            total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
            return max(0.001, total_seconds)  # Minimum 1ms
        except ValueError:
            return 1.0  # Default to 1 second if invalid input
    
    def start_clicking(self):
        if self.clicking:
            self.stop_clicking()
            return
        
        try:
            interval = self.get_interval()
            if interval <= 0:
                messagebox.showerror("Error", "Click interval must be greater than 0")
                return
            
            self.clicking = True
            self.click_count = 0
            self.update_button_texts()
            self.stop_btn.configure(state="normal")
            
            # Start idle mode monitoring if enabled
            if self.idle_mode_enabled:
                self.start_idle_monitoring()
            
            if self.enable_status_frame:
                self.status_label.configure(text="🔥 Clicking...")
            
            # Update idle status
            self.update_idle_status()
            
            # Start clicking in a separate thread
            self.click_thread = threading.Thread(target=self.click_worker, daemon=True)
            self.click_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error starting clicker: {e}")
    
    def stop_clicking(self, event=None):
        if not self.clicking:
            return
        
        self.clicking = False
        self.update_button_texts()
        self.stop_btn.configure(state="disabled")
        
        # Stop idle mode monitoring
        if self.idle_mode_enabled:
            self.stop_idle_monitoring()
            # Restart monitoring for next session
            self.start_idle_monitoring()
        
        # Update idle status
        self.update_idle_status()
        
        if self.enable_status_frame:
            self.status_label.configure(text="⏹️ Stopped")
    
    def toggle_clicking(self, event=None):
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()
    
    def click_worker(self):
        interval = self.get_interval()
        button = self.button_var.get()
        repeat_forever = self.repeat_var.get() == "forever"
        
        try:
            max_clicks = int(self.times_var.get() or 0) if not repeat_forever else 0
        except ValueError:
            max_clicks = 0
        
        # Get click position
        if self.location_var.get() == "current":
            click_x, click_y = pyautogui.position()
        else:
            try:
                click_x = int(self.x_var.get() or 0)
                click_y = int(self.y_var.get() or 0)
            except ValueError:
                click_x, click_y = pyautogui.position()
        
        last_click_time = 0
        last_ui_update = 0
        
        while self.clicking:
            try:
                # Check if we should stop (max clicks reached)
                if not repeat_forever and self.click_count >= max_clicks:
                    break
                
                current_time = time.time()
                
                # Check if we should pause for user activity (idle mode)
                if self.should_pause_for_activity():
                    # Update idle status less frequently to reduce lag
                    if current_time - last_ui_update > 0.2:  # Update UI every 200ms
                        self.root.after(0, self.update_idle_status)
                        last_ui_update = current_time
                    
                    # Wait a bit and continue checking
                    time.sleep(0.05)  # Reduced sleep for better responsiveness
                    continue
                
                # Check if enough time has passed since last click
                if current_time - last_click_time < interval:
                    # Update idle status less frequently to reduce lag
                    if current_time - last_ui_update > 0.2:  # Update UI every 200ms
                        self.root.after(0, self.update_idle_status)
                        last_ui_update = current_time
                    
                    # Wait a bit and continue
                    time.sleep(0.05)  # Reduced sleep for better responsiveness
                    continue
                
                # Perform click
                if self.location_var.get() == "current":
                    pyautogui.click(button=button)
                else:
                    pyautogui.click(click_x, click_y, button=button)
                
                self.click_count += 1
                last_click_time = current_time
                
                # Update UI less frequently to reduce lag
                if current_time - last_ui_update > 0.2:  # Update UI every 200ms
                    self.root.after(0, self.update_ui)
                    self.root.after(0, self.update_idle_status)
                    last_ui_update = current_time
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.01)
                
            except pyautogui.FailSafeException:
                self.root.after(0, self.emergency_stop)
                break
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Click error: {e}"))
                break
        
        # Stop clicking when done
        self.root.after(0, self.stop_clicking)
    
    def update_ui(self):
        if self.enable_status_frame:
            self.clicks_label.configure(text=f"Clicks: {self.click_count}")
            
            if self.repeat_var.get() == "times":
                try:
                    max_clicks = int(self.times_var.get() or 0)
                    progress = f" ({self.click_count}/{max_clicks})"
                    self.status_label.configure(text=f"🔥 Clicking...{progress}")
                except ValueError:
                    self.status_label.configure(text="🔥 Clicking...")
    
    def emergency_stop(self):
        self.stop_clicking()
        messagebox.showwarning("Emergency Stop", 
                             "⚠️ Clicking stopped due to mouse movement to top-left corner")
    
    def run(self):
        # Setup cleanup on close
        def on_closing():
            # Auto-save current configuration
            self.auto_save_configuration()
            
            self.cleanup_hotkeys()
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the GUI
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.auto_save_configuration()
            self.cleanup_hotkeys()
        finally:
            self.cleanup_hotkeys()
    
    def on_idle_detection_change(self):
        """Handle changes to idle mode detection setting"""
        self.idle_mode_enabled = self.idle_detection_var.get()
        
        if self.idle_mode_enabled:
            self.start_idle_monitoring()
            self.idle_status_label.configure(
                text="🟢 Idle mode enabled - clicks only when no mouse/keyboard activity",
                text_color="green"
            )
        else:
            self.stop_idle_monitoring()
            self.idle_status_label.configure(
                text="🔘 Idle mode disabled",
                text_color="gray"
            )
    
    def start_idle_monitoring(self):
        """Start monitoring mouse and keyboard activity"""
        if not self.idle_mode_enabled:
            return
            
        if self.mouse_movement_listener or self.keyboard_listener:
            self.stop_idle_monitoring()
        
        self.last_mouse_position = pyautogui.position()
        self.last_activity_time = time.time()
        
        # Start mouse movement listener
        self.mouse_movement_listener = mouse.Listener(on_move=self.on_mouse_move, suppress=False)
        self.mouse_movement_listener.start()
        
        # Start keyboard listener with minimal overhead
        try:
            self.keyboard_listener = pynput_keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release,
                suppress=False
            )
            self.keyboard_listener.start()
        except Exception as e:
            print(f"Keyboard listener failed: {e}")
            # If pynput keyboard fails, we'll only monitor mouse
    
    def stop_idle_monitoring(self):
        """Stop monitoring mouse and keyboard activity"""
        if self.mouse_movement_listener:
            self.mouse_movement_listener.stop()
            self.mouse_movement_listener = None
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
    
    def on_mouse_move(self, x, y):
        """Handle mouse movement events"""
        if self.idle_mode_enabled:
            current_time = time.time()
            
            # Only update if enough time has passed AND mouse moved significantly
            if (current_time - self.last_activity_time > 0.1 and 
                (self.last_mouse_position is None or 
                 abs(x - self.last_mouse_position[0]) > 5 or 
                 abs(y - self.last_mouse_position[1]) > 5)):
                self.last_mouse_position = (x, y)
                self.last_activity_time = current_time
    
    def on_key_press(self, key):
        """Handle keyboard press events"""
        if self.idle_mode_enabled:
            current_time = time.time()
            
            # Only update if enough time has passed to avoid excessive updates
            if current_time - self.last_activity_time > 0.1:  # Throttle to 10 times per second
                self.last_activity_time = current_time
    
    def on_key_release(self, key):
        """Handle keyboard release events"""
        if self.idle_mode_enabled:
            current_time = time.time()
            
            # Only update if enough time has passed to avoid excessive updates  
            if current_time - self.last_activity_time > 0.1:  # Throttle to 10 times per second
                self.last_activity_time = current_time
    
    def should_pause_for_activity(self):
        """Check if clicking should be paused due to recent user activity"""
        if not self.idle_mode_enabled:
            return False
        
        try:
            delay = float(self.idle_delay_var.get() or 1.0)
        except ValueError:
            delay = 1.0
        
        time_since_activity = time.time() - self.last_activity_time
        return time_since_activity < delay
    
    def update_idle_status(self):
        """Update idle status label"""
        if not self.idle_mode_enabled:
            return
        
        if self.clicking:
            if self.should_pause_for_activity():
                # Check if status needs to be updated to avoid unnecessary UI updates
                current_text = self.idle_status_label.cget("text")
                if "paused" not in current_text:
                    self.idle_status_label.configure(
                        text="🔴 Clicks paused - waiting for user to become idle",
                        text_color="red"
                    )
            else:
                # Check if status needs to be updated to avoid unnecessary UI updates
                current_text = self.idle_status_label.cget("text")
                if "normally" not in current_text:
                    self.idle_status_label.configure(
                        text="🟢 Clicking normally - user is idle",
                        text_color="green"
                    )
        else:
            # Check if status needs to be updated to avoid unnecessary UI updates
            current_text = self.idle_status_label.cget("text")
            if "enabled" not in current_text or "only when no" not in current_text:
                self.idle_status_label.configure(
                    text="🟢 Idle mode enabled - clicks only when no mouse/keyboard activity",
                    text_color="green"
                )
    
    def save_configuration(self, filename=None, show_message_box=True):
        """Save current configuration to JSON file"""
        try:
            # Get current configuration
            config = {
                "click_interval": {
                    "hours": self.hours_var.get(),
                    "minutes": self.minutes_var.get(),
                    "seconds": self.seconds_var.get(),
                    "milliseconds": self.milliseconds_var.get()
                },
                "mouse_button": self.button_var.get(),
                "click_repeat": {
                    "mode": self.repeat_var.get(),
                    "times": self.times_var.get()
                },
                "click_location": {
                    "mode": self.location_var.get(),
                    "x": self.x_var.get(),
                    "y": self.y_var.get()
                },
                "idle_mode_detection": {
                    "enabled": self.idle_detection_var.get(),
                    "delay": self.idle_delay_var.get()
                },
                "hotkeys": {
                    "start_stop": self.hotkey_start,
                    "stop": self.hotkey_stop
                },
                "version": "1.0"
            }
            
            if filename is None:
                # Ask user for filename
                config_dir = get_config_directory()
                filename = filedialog.asksaveasfilename(
                    title="Save Configuration",
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    initialdir=config_dir
                )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                
                if show_message_box:
                    messagebox.showinfo("Success", f"Configuration saved successfully:\n{os.path.basename(filename)}")
                return True
            return False
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving configuration:\n{e}")
            return False
    
    def load_configuration(self, filename=None, show_message_box=True):
        """Load configuration from JSON file"""
        try:
            if filename is None:
                # Ask user for filename
                config_dir = get_config_directory()
                filename = filedialog.askopenfilename(
                    title="Load Configuration",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    initialdir=config_dir
                )
            
            if not filename:
                return False
            
            with open(filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Apply configuration
            # Click interval
            if "click_interval" in config:
                interval = config["click_interval"]
                self.hours_var.set(interval.get("hours", "0"))
                self.minutes_var.set(interval.get("minutes", "0"))
                self.seconds_var.set(interval.get("seconds", "1"))
                self.milliseconds_var.set(interval.get("milliseconds", "0"))
            
            # Mouse button
            if "mouse_button" in config:
                self.button_var.set(config["mouse_button"])
            
            # Click repeat
            if "click_repeat" in config:
                repeat = config["click_repeat"]
                self.repeat_var.set(repeat.get("mode", "forever"))
                self.times_var.set(repeat.get("times", "100"))
                self.on_repeat_change()  # Update UI state
            
            # Click location
            if "click_location" in config:
                location = config["click_location"]
                self.location_var.set(location.get("mode", "current"))
                self.x_var.set(location.get("x", "0"))
                self.y_var.set(location.get("y", "0"))
                self.on_location_change()  # Update UI state
            
            # Idle mode detection (backwards compatibility)
            if "idle_mode_detection" in config:
                idle_mode = config["idle_mode_detection"]
                self.idle_detection_var.set(idle_mode.get("enabled", False))
                self.idle_delay_var.set(idle_mode.get("delay", "1.0"))
                self.on_idle_detection_change()  # Update UI state
            elif "mouse_movement_detection" in config:
                # Backwards compatibility with old configs
                movement = config["mouse_movement_detection"]
                self.idle_detection_var.set(movement.get("enabled", False))
                self.idle_delay_var.set(movement.get("delay", "1.0"))
                self.on_idle_detection_change()  # Update UI state
            
            # Hotkeys
            if "hotkeys" in config:
                hotkeys = config["hotkeys"]
                self.hotkey_start = hotkeys.get("start_stop", "f6")
                self.hotkey_stop = hotkeys.get("stop", "f7")
                self.setup_global_hotkeys()
                self.update_button_texts()
            
            if show_message_box:
                messagebox.showinfo("Success", f"Configuration loaded successfully:\n{os.path.basename(filename)}")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading configuration:\n{e}")
            return False
    
    def create_configurations_window(self):
        """Create and show the configurations management window"""
        config_window = ctk.CTkToplevel(self.root)
        config_window.title("💾 Manage Configurations")
        config_window.geometry("500x400")
        config_window.resizable(False, False)

        config_window.transient(self.root)
        config_window.grab_set()
        config_window.focus_force()

        # Centralizar em relação à janela principal
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (500 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (400 // 2)
        config_window.geometry(f"+{x}+{y}")

        # Main frame
        main_frame = ctk.CTkFrame(config_window, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="💾 Manage Configurations",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 10))

        # Instructions
        instructions_label = ctk.CTkLabel(
            main_frame,
            text="Save and load different auto clicker configurations",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        instructions_label.pack(pady=(0, 20))

        # Current configuration preview
        preview_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        preview_frame.pack(fill="x", padx=20, pady=(0, 20))

        preview_title = ctk.CTkLabel(
            preview_frame,
            text="📋 Current Configuration:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        preview_title.pack(pady=(15, 10))

        # Create preview text
        interval_text = f"{self.hours_var.get()}h {self.minutes_var.get()}m {self.seconds_var.get()}s {self.milliseconds_var.get()}ms"
        location_text = f"{self.location_var.get()}" + (f" ({self.x_var.get()}, {self.y_var.get()})" if self.location_var.get() == "pick" else "")
        repeat_text = f"{self.repeat_var.get()}" + (f" ({self.times_var.get()}x)" if self.repeat_var.get() == "times" else "")
        
        preview_text = f"""• Interval: {interval_text}
        • Button: {self.button_var.get()}
        • Repeat: {repeat_text}
        • Location: {location_text}
        • Movement Detection: {"Enabled" if self.movement_detection_var.get() else "Disabled"}
        • Hotkeys: {self.hotkey_start.upper()} / {self.hotkey_stop.upper()}"""

        preview_label = ctk.CTkLabel(
            preview_frame,
            text=preview_text,
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        preview_label.pack(pady=(0, 15), padx=15)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Save button
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Save Configuration",
            command=self.save_configuration,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_btn.pack(fill="x", padx=15, pady=15)

        # Load button
        load_btn = ctk.CTkButton(
            buttons_frame,
            text="📂 Load Configuration",
            command=self.load_configuration,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        load_btn.pack(fill="x", padx=15, pady=(0, 15))

        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="✅ Close",
            command=config_window.destroy,
            height=35,
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        close_btn.pack(pady=(0, 20))

    def auto_save_configuration(self):
        """Auto-save current configuration to default file"""
        try:
            config_dir = get_config_directory()
            default_config_file = os.path.join(config_dir, "last_config.json")
            return self.save_configuration(default_config_file, show_message_box=False)
        except Exception as e:
            print(f"Error auto-saving configuration: {e}")
            return False
    
    def auto_load_configuration(self):
        """Auto-load configuration from default file if it exists"""
        try:
            config_dir = get_config_directory()
            default_config_file = os.path.join(config_dir, "last_config.json")
            
            if os.path.exists(default_config_file):
                return self.load_configuration(default_config_file, show_message_box=False)
            return False
        except Exception as e:
            print(f"Error auto-loading configuration: {e}")
            return False
    
