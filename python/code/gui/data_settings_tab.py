import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path


# Configuration file path
CONFIG_DIR = Path.home() / ".iremoteengineer"
CONFIG_FILE = CONFIG_DIR / "data_settings.json"

# Data group descriptions
DATA_GROUP_DESCRIPTIONS = {
    "lap_finish": "Detects when you cross the finish line and then sends data including:\n• Session info\n• Fuel consumption\n• Lap time history",
    "relative": "Real-time position data relative to other cars. Includes:\n• Cars positions\n• Gap times\n• Position in class\n• Overall position\n• Distance to cars\n• New lap times\n• Current drivers",
    "weather": "Current weather and track conditions. Includes:\n• Air temperature\n• Track temperature\n• Wind speed and direction\n• Precipitation\n• Track wetness level",
    "incidents": "Incident and penalty information. Includes:\n• Incident count\n• Total incident points",
    "tow": "Checks if the car is being towed.",
    "tyres": "Tire wear and temperature data. Includes:• Tire temperature\n• Tire wear percentage",
    "pit": "Checks if performing a pit stop and if taking a fast repair."
}


class ToolTip:
    """
    Create a tooltip for a given widget with hover delay
    """
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.schedule_id = None
        
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Button>", self.on_leave)
    
    def on_enter(self, event=None):
        """Schedule tooltip to appear after delay"""
        self.schedule_id = self.widget.after(self.delay, self.show_tooltip)
    
    def on_leave(self, event=None):
        """Cancel scheduled tooltip and hide if visible"""
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None
        self.hide_tooltip()
    
    def show_tooltip(self):
        """Display the tooltip"""
        if self.tooltip_window or not self.text:
            return
        
        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Create tooltip content
        frame = ttk.Frame(self.tooltip_window, relief=tk.SOLID, borderwidth=1)
        frame.pack()
        
        label = ttk.Label(
            frame,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            foreground="#000000",
            relief=tk.FLAT,
            padding=(8, 5)
        )
        label.pack()
    
    def hide_tooltip(self):
        """Hide the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


# Default settings
DEFAULT_SETTINGS = {
    "lap_finish": {
        "enabled": True,
        "mode": "interval",  # Fixed to interval for lap detection
        "interval": 10
    },
    "relative": {
        "enabled": True,
        "mode": "interval",
        "interval": 5
    },
    "weather": {
        "enabled": True,
        "mode": "interval",
        "interval": 30
    },
    "tow": {
        "enabled": True,
        "mode": "interval",
        "interval": 15
    },
    "incidents": {
        "enabled": True,
        "mode": "interval",
        "interval": 15
    },
    "tyres": {
        "enabled": True,
        "mode": "interval",
        "interval": 20
    },
    "pit": {
        "enabled": True,
        "mode": "interval",
        "interval": 10
    }
}


def load_intervals():
    """Load settings from JSON file or return defaults if file doesn't exist"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        else:
            return DEFAULT_SETTINGS.copy()
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """Save settings to JSON file"""
    try:
        # Create config directory if it doesn't exist
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


class DataGroupWidget(ttk.Frame):
    """Widget for configuring a single data group"""
    
    def __init__(self, parent, group_name, settings):
        super().__init__(parent)
        self.group_name = group_name
        
        # Variables
        self.enabled_var = tk.BooleanVar(value=settings.get("enabled", True))
        self.mode_var = tk.StringVar(value=settings.get("mode", "interval"))
        self.interval_var = tk.StringVar(value=str(settings.get("interval", 10)))
        
        # Flag to track if lap mode should be globally disabled
        self._lap_mode_disabled = False
        
        # Create UI
        self.create_widgets()
        
        # Bind events to update state
        self.enabled_var.trace_add("write", self.update_state)
        self.mode_var.trace_add("write", self.update_state)
        
        # Initial state update
        self.update_state()
    
    def create_widgets(self):
        """Create the widgets for this data group"""
        # Main container
        container = ttk.Frame(self, relief=tk.RIDGE, borderwidth=1, padding="10")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Header row with name and enable toggle
        header_frame = ttk.Frame(container)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Left side: Group name and enable checkbox
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side=tk.LEFT)
        
        # Group name
        name_label = ttk.Label(
            left_frame, 
            text=self.group_name.replace("_", " ").title(),
            font=("Helvetica", 10, "bold")
        )
        name_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Enable/Disable toggle
        self.enable_check = ttk.Checkbutton(
            left_frame,
            text="Enabled",
            variable=self.enabled_var
        )
        self.enable_check.pack(side=tk.LEFT)
        
        # Right side: Info icon
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # Info icon (using Unicode symbol)
        info_label = ttk.Label(
            right_frame,
            text="ℹ️",
            font=("Helvetica", 14),
            cursor="question_arrow",
            foreground="#1976d2"
        )
        info_label.pack(side=tk.RIGHT)
        
        # Add tooltip to info icon
        description = DATA_GROUP_DESCRIPTIONS.get(self.group_name, "No description available")
        ToolTip(info_label, description, delay=300)
        
        # For lap_finish, mode is always "interval" and cannot be changed
        if self.group_name == "lap_finish":
            # Show info message instead of mode selection
            info_text = ttk.Label(
                container, 
                text="Transmission Mode: Interval-based (fixed - used to detect lap completion)",
                foreground="gray",
                font=("Helvetica", 9, "italic")
            )
            info_text.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
            
            # Store references as None since they don't exist for lap_finish
            self.interval_radio = None
            self.lap_radio = None
            
            # Interval setting for lap_finish
            interval_label = ttk.Label(container, text="Interval (seconds):")
            interval_label.grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            
            # Validate command for numeric input
            vcmd = (self.register(self.validate_interval), '%P')
            
            self.interval_entry = ttk.Entry(
                container,
                textvariable=self.interval_var,
                width=10,
                validate='key',
                validatecommand=vcmd
            )
            self.interval_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
            
            seconds_label = ttk.Label(container, text="sec")
            seconds_label.grid(row=2, column=2, sticky=tk.W, pady=5, padx=(5, 0))
        else:
            # Mode selection for other data groups
            mode_label = ttk.Label(container, text="Transmission Mode:")
            mode_label.grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            
            mode_frame = ttk.Frame(container)
            mode_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
            
            self.interval_radio = ttk.Radiobutton(
                mode_frame,
                text="Interval-based",
                variable=self.mode_var,
                value="interval"
            )
            self.interval_radio.pack(side=tk.LEFT, padx=(0, 15))
            
            self.lap_radio = ttk.Radiobutton(
                mode_frame,
                text="End of lap",
                variable=self.mode_var,
                value="lap"
            )
            self.lap_radio.pack(side=tk.LEFT)
            
            # Interval setting
            interval_label = ttk.Label(container, text="Interval (seconds):")
            interval_label.grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            
            # Validate command for numeric input
            vcmd = (self.register(self.validate_interval), '%P')
            
            self.interval_entry = ttk.Entry(
                container,
                textvariable=self.interval_var,
                width=10,
                validate='key',
                validatecommand=vcmd
            )
            self.interval_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
            
            seconds_label = ttk.Label(container, text="sec")
            seconds_label.grid(row=2, column=2, sticky=tk.W, pady=5, padx=(5, 0))
    
    def validate_interval(self, value):
        """Validate that input is a positive integer or empty"""
        if value == "":
            return True
        try:
            int_value = int(value)
            return int_value > 0 and int_value <= 3600  # Max 1 hour
        except ValueError:
            return False
    
    def update_state(self, *args):
        """Update widget states based on enabled status and mode"""
        enabled = self.enabled_var.get()
        mode = self.mode_var.get()
        
        # lap_finish only has interval entry, no mode selection
        if self.group_name == "lap_finish":
            interval_state = tk.NORMAL if enabled else tk.DISABLED
            self.interval_entry.config(state=interval_state)
            return
        
        # Enable/disable mode radios based on enabled state
        state = tk.NORMAL if enabled else tk.DISABLED
        self.interval_radio.config(state=state)
        
        # For lap_radio, check if it should be disabled (stored in widget)
        if hasattr(self, '_lap_mode_disabled') and self._lap_mode_disabled:
            self.lap_radio.config(state=tk.DISABLED)
        else:
            self.lap_radio.config(state=state)
        
        # Enable/disable interval entry based on enabled state and mode
        interval_state = tk.NORMAL if (enabled and mode == "interval") else tk.DISABLED
        self.interval_entry.config(state=interval_state)
    
    def get_settings(self):
        """Get current settings as a dictionary"""
        interval_str = self.interval_var.get()
        interval = int(interval_str) if interval_str else 10
        
        # For lap_finish, mode is always "interval"
        if self.group_name == "lap_finish":
            return {
                "enabled": self.enabled_var.get(),
                "mode": "interval",
                "interval": interval
            }
        
        return {
            "enabled": self.enabled_var.get(),
            "mode": self.mode_var.get(),
            "interval": interval
        }
    
    def set_lap_mode_state(self, state):
        """Enable or disable the 'End of lap' radio button"""
        if self.lap_radio:  # Only for non-lap_finish groups
            # Store flag to indicate lap mode should be globally disabled
            self._lap_mode_disabled = (state == tk.DISABLED)
            
            # If disabling and currently on lap mode, switch to interval
            if state == tk.DISABLED and self.mode_var.get() == "lap":
                self.mode_var.set("interval")
            
            # Apply the state
            self.lap_radio.config(state=state)


def get_data_settings_tab(notebook):
    """
    Creates and returns the data settings tab frame.
    
    Args:
        notebook: The parent ttk.Notebook widget
        
    Returns:
        ttk.Frame: The configured data settings tab frame
    """
    frame = ttk.Frame(notebook)
    
    # Main container with padding
    main_container = ttk.Frame(frame, padding="20")
    main_container.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk.Label(
        main_container, 
        text="Data Transmission Settings", 
        font=("Helvetica", 16, "bold")
    )
    title_label.pack(pady=(0, 10))
    
    # Description
    desc_label = ttk.Label(
        main_container,
        text="Configure how and when each data group is transmitted to the lobby",
        font=("Helvetica", 9),
        foreground="gray"
    )
    desc_label.pack(pady=(0, 20))
    
    # Scrollable frame for data groups
    canvas = tk.Canvas(main_container, highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack scrollbar and canvas
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Load current settings
    current_settings = load_intervals()
    
    # Create data group widgets
    data_groups = {}
    for group_name in ["lap_finish", "relative", "weather", "incidents", "tyres", "pit", "tow"]:
        group_settings = current_settings.get(group_name, DEFAULT_SETTINGS[group_name])
        widget = DataGroupWidget(scrollable_frame, group_name, group_settings)
        widget.pack(fill=tk.X, pady=5, padx=5)
        data_groups[group_name] = widget
    
    # Function to update lap mode availability based on lap_finish state
    def update_lap_mode_availability(*args):
        """Enable/disable 'End of lap' options based on lap_finish enabled state"""
        lap_finish_enabled = data_groups["lap_finish"].enabled_var.get()
        state = tk.NORMAL if lap_finish_enabled else tk.DISABLED
        
        # Update all other data groups
        for group_name, widget in data_groups.items():
            if group_name != "lap_finish":
                widget.set_lap_mode_state(state)
    
    # Bind lap_finish enabled state to update other widgets
    data_groups["lap_finish"].enabled_var.trace_add("write", update_lap_mode_availability)
    
    # Initial state update
    update_lap_mode_availability()
    
    # Button frame at the bottom
    button_frame = ttk.Frame(frame, padding="20")
    button_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Status label
    status_label = ttk.Label(button_frame, text="", foreground="green")
    status_label.pack(side=tk.LEFT, padx=(0, 20))
    
    def apply_settings():
        """Apply and save the current settings"""
        # Validate all intervals
        for group_name, widget in data_groups.items():
            settings = widget.get_settings()
            if settings["enabled"] and settings["mode"] == "interval":
                if settings["interval"] <= 0:
                    messagebox.showerror(
                        "Invalid Interval",
                        f"Please enter a valid interval for {group_name.replace('_', ' ').title()}"
                    )
                    return
        
        # Collect all settings
        new_settings = {}
        for group_name, widget in data_groups.items():
            new_settings[group_name] = widget.get_settings()
        
        # Save to file
        if save_settings(new_settings):
            status_label.config(text="✓ Settings saved successfully", foreground="green")
            # Clear status message after 3 seconds
            frame.after(3000, lambda: status_label.config(text=""))
        else:
            messagebox.showerror("Error", "Failed to save settings")
            status_label.config(text="✗ Failed to save settings", foreground="red")
    
    def reset_defaults():
        """Reset all settings to defaults"""
        result = messagebox.askyesno(
            "Reset to Defaults",
            "Are you sure you want to reset all settings to their default values?"
        )
        if result:
            # Reload the tab with default settings
            for group_name, widget in data_groups.items():
                default = DEFAULT_SETTINGS[group_name]
                widget.enabled_var.set(default["enabled"])
                widget.mode_var.set(default["mode"])
                widget.interval_var.set(str(default["interval"]))
            status_label.config(text="Settings reset to defaults (not saved)", foreground="orange")
    
    # Buttons
    apply_button = ttk.Button(
        button_frame,
        text="Apply Settings",
        command=apply_settings,
        width=15
    )
    apply_button.pack(side=tk.RIGHT, padx=(5, 0))
    
    reset_button = ttk.Button(
        button_frame,
        text="Reset to Defaults",
        command=reset_defaults,
        width=15
    )
    reset_button.pack(side=tk.RIGHT)
    
    return frame
