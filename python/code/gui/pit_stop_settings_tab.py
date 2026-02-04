import tkinter as tk
from tkinter import ttk
import json
import logging
from pathlib import Path

# Configuration file path
CONFIG_DIR = Path.home() / ".iremoteengineer"
CONFIG_FILE = CONFIG_DIR / "pit_settings.json"

# Default settings
DEFAULT_SETTINGS = {
    "remote_pit_control_enabled": False,
    "fuel_management_enabled": False,
    "tyre_swap_enabled": False,
    "tyre_compound_enabled": False,
}


def load_pit_settings():
    """Load pit settings from JSON file or return defaults if file doesn't exist"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        else:
            return DEFAULT_SETTINGS.copy()
    except Exception as e:
        logging.error(f"Error loading pit settings: {e}")
        return DEFAULT_SETTINGS.copy()


def save_pit_settings(settings):
    """Save pit settings to JSON file"""
    try:
        # Create config directory if it doesn't exist
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        with open(CONFIG_FILE, "w") as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        logging.error(f"Error saving pit settings: {e}")
        return False


class PitSettingsWidget(ttk.Frame):
    """Widget for configuring pit stop management settings"""

    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings

        # Variables
        self.remote_control_var = tk.BooleanVar(
            value=settings.get("remote_pit_control_enabled", False)
        )
        self.fuel_var = tk.BooleanVar(
            value=settings.get("fuel_management_enabled", False)
        )
        self.tyre_swap_var = tk.BooleanVar(
            value=settings.get("tyre_swap_enabled", False)
        )
        self.tyre_compound_var = tk.BooleanVar(
            value=settings.get("tyre_compound_enabled", False)
        )

        # Create UI
        self.create_widgets()

        # Bind events to update state
        self.remote_control_var.trace_add("write", self.update_state)

        # Initial state update
        self.update_state()

    def create_widgets(self):
        """Create the widgets for pit settings"""
        # Main container
        container = ttk.Frame(self, relief=tk.RIDGE, borderwidth=1, padding="15")
        container.pack(fill=tk.BOTH, expand=True)

        # Master toggle
        master_frame = ttk.Frame(container)
        master_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        master_label = ttk.Label(
            master_frame, text="Remote Pit Stop Control", font=("Helvetica", 12, "bold")
        )
        master_label.pack(side=tk.LEFT)

        self.master_check = ttk.Checkbutton(
            master_frame,
            text="Allow remote pit stop management",
            variable=self.remote_control_var,
        )
        self.master_check.pack(side=tk.LEFT, padx=(20, 0))

        # Info label
        info_label = ttk.Label(
            container,
            text="Enable remote control to allow pit stop commands from the web interface",
            foreground="gray",
            font=("Helvetica", 9, "italic"),
        )
        info_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 20))

        # Separator
        separator = ttk.Separator(container, orient=tk.HORIZONTAL)
        separator.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        # Sub-options label
        options_label = ttk.Label(
            container, text="Allowed Operations", font=("Helvetica", 10, "bold")
        )
        options_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))

        # Fuel management
        fuel_frame = ttk.Frame(container)
        fuel_frame.grid(row=4, column=0, sticky=tk.W, pady=5)

        self.fuel_check = ttk.Checkbutton(
            fuel_frame, text="Fuel Management", variable=self.fuel_var
        )
        self.fuel_check.pack(side=tk.LEFT)

        fuel_desc = ttk.Label(
            fuel_frame,
            text="  -  Allow remote fuel amount adjustments",
            foreground="gray",
            font=("Helvetica", 9),
        )
        fuel_desc.pack(side=tk.LEFT)

        # Tyre swap
        tyre_swap_frame = ttk.Frame(container)
        tyre_swap_frame.grid(row=5, column=0, sticky=tk.W, pady=5)

        self.tyre_swap_check = ttk.Checkbutton(
            tyre_swap_frame, text="Tyre Changes", variable=self.tyre_swap_var
        )
        self.tyre_swap_check.pack(side=tk.LEFT)

        tyre_swap_desc = ttk.Label(
            tyre_swap_frame,
            text="  -  Allow remote tyre change requests (LF, RF, LR, RR)",
            foreground="gray",
            font=("Helvetica", 9),
        )
        tyre_swap_desc.pack(side=tk.LEFT)

        # Tyre compound
        tyre_compound_frame = ttk.Frame(container)
        tyre_compound_frame.grid(row=6, column=0, sticky=tk.W, pady=5)

        self.tyre_compound_check = ttk.Checkbutton(
            tyre_compound_frame,
            text="Tyre Compound Selection",
            variable=self.tyre_compound_var,
        )
        self.tyre_compound_check.pack(side=tk.LEFT)

        tyre_compound_desc = ttk.Label(
            tyre_compound_frame,
            text="  -  Allow remote tyre compound changes (wet/dry)",
            foreground="gray",
            font=("Helvetica", 9),
        )
        tyre_compound_desc.pack(side=tk.LEFT)

        # Warning message
        warning_frame = ttk.Frame(container)
        warning_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(20, 0))

        warning_icon = ttk.Label(
            warning_frame, text="\u26a0", font=("Helvetica", 14), foreground="#ff6b00"
        )
        warning_icon.pack(side=tk.LEFT, padx=(0, 10))

        warning_text = ttk.Label(
            warning_frame,
            text="Warning: Enabling remote pit control allows anyone with access to your lobby\n"
            "to send pit stop commands to your car. Only enable this if you trust all lobby members.",
            foreground="#ff6b00",
            font=("Helvetica", 9),
            wraplength=500,
            justify=tk.LEFT,
        )
        warning_text.pack(side=tk.LEFT)

    def update_state(self, *args):
        """Update widget states based on master toggle"""
        enabled = self.remote_control_var.get()

        # Enable/disable sub-options based on master toggle
        state = tk.NORMAL if enabled else tk.DISABLED
        self.fuel_check.config(state=state)
        self.tyre_swap_check.config(state=state)
        self.tyre_compound_check.config(state=state)

        # If master is disabled, uncheck all sub-options
        if not enabled:
            self.fuel_var.set(False)
            self.tyre_swap_var.set(False)
            self.tyre_compound_var.set(False)

    def get_settings(self):
        """Get current settings as a dictionary"""
        return {
            "remote_pit_control_enabled": self.remote_control_var.get(),
            "fuel_management_enabled": self.fuel_var.get(),
            "tyre_swap_enabled": self.tyre_swap_var.get(),
            "tyre_compound_enabled": self.tyre_compound_var.get(),
        }


def get_pit_settings_tab(notebook, status_bar):
    """
    Creates and returns the pit settings tab frame.

    Args:
        notebook: The parent ttk.Notebook widget
        status_bar: The StatusBar widget for displaying status messages

    Returns:
        ttk.Frame: The configured pit settings tab frame
    """
    frame = ttk.Frame(notebook)

    # Button frame at the bottom (pack first so it stays at bottom)
    button_frame = ttk.Frame(frame, padding="20")
    button_frame.pack(side=tk.BOTTOM, fill=tk.X)

    # Main container with padding
    main_container = ttk.Frame(frame, padding="20")
    main_container.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(
        main_container, text="Pit Stop Control Settings", font=("Helvetica", 16, "bold")
    )
    title_label.pack(pady=(0, 10))

    # Description
    desc_label = ttk.Label(
        main_container,
        text="Configure remote pit stop management permissions for your lobby",
        font=("Helvetica", 9),
        foreground="gray",
    )
    desc_label.pack(pady=(0, 20))

    # Load current settings
    current_settings = load_pit_settings()

    # Create pit settings widget
    pit_widget = PitSettingsWidget(main_container, current_settings)
    pit_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

    # Status label
    status_label = ttk.Label(button_frame, text="", foreground="green")
    status_label.pack(side=tk.LEFT, padx=(0, 20))

    def apply_settings():
        """Apply and save the current settings"""
        new_settings = pit_widget.get_settings()

        # Save to file
        if save_pit_settings(new_settings):
            status_label.config(
                text="\u2713 Settings saved successfully", foreground="green"
            )
            # Clear status message after 3 seconds
            frame.after(3000, lambda: status_label.config(text=""))
        else:
            status_bar.set_status("Failed to save settings", "error")
            status_label.config(text="\u2717 Failed to save settings", foreground="red")

    def reset_defaults():
        """Reset all settings to defaults"""
        pit_widget.remote_control_var.set(
            DEFAULT_SETTINGS["remote_pit_control_enabled"]
        )
        pit_widget.fuel_var.set(DEFAULT_SETTINGS["fuel_management_enabled"])
        pit_widget.tyre_swap_var.set(DEFAULT_SETTINGS["tyre_swap_enabled"])
        pit_widget.tyre_compound_var.set(DEFAULT_SETTINGS["tyre_compound_enabled"])
        status_label.config(
            text="Settings reset to defaults (not saved)", foreground="orange"
        )

    # Buttons
    apply_button = ttk.Button(
        button_frame, text="Apply Settings", command=apply_settings, width=15
    )
    apply_button.pack(side=tk.RIGHT, padx=(5, 0))

    reset_button = ttk.Button(
        button_frame, text="Reset to Defaults", command=reset_defaults, width=15
    )
    reset_button.pack(side=tk.RIGHT)

    return frame
