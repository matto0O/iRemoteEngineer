import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import logging

from gui.streaming_tab import get_streaming_tab, is_streaming
from gui.data_settings_tab import get_data_settings_tab
from gui.pit_stop_settings_tab import get_pit_settings_tab
from gui.log_handler import GUILogHandler


class IracingDataGUI:
    def __init__(self, root, debug=False):
        self.debug = debug
        self.root = root
        self.root.title("iRemoteEngineer")
        self.root.geometry("600x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create notebook for sections
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Streaming tab
        self.streaming_frame = get_streaming_tab(self.notebook, debug=self.debug)
        self.notebook.add(self.streaming_frame, text="Streaming")

        # Data Settings tab
        self.data_settings_frame = get_data_settings_tab(self.notebook)
        self.notebook.add(self.data_settings_frame, text="Data Settings")

        # Pit-stop tab
        self.pit_settings_frame = get_pit_settings_tab(self.notebook)
        self.notebook.add(self.pit_settings_frame, text="Pit Settings")

        # # System Settings tab
        # self.system_settings_frame = ttk.Frame(self.notebook)
        # self.notebook.add(self.system_settings_frame, text="System Settings")
        # ttk.Label(self.system_settings_frame, text="System Settings Configuration").pack(pady=10)

        # Logs tab
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Logs")
        self.log_text = scrolledtext.ScrolledText(
            self.logs_frame, wrap=tk.WORD, height=20, state="disabled"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Set up logging to GUI
        self.setup_logging()

    def setup_logging(self):
        """Configure logging to write to the GUI log widget"""
        # Create GUI handler
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setLevel(logging.INFO)

        # Get root logger and configure it
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # Remove any existing handlers to avoid duplicates
        root_logger.handlers.clear()

        # Add our GUI handler
        root_logger.addHandler(gui_handler)

        # Log initial message
        logging.info("iRemoteEngineer logging initialized")

    def on_close(self):
        if is_streaming():
            messagebox.showwarning(
                "Cannot close",
                "The stream is still running. Please stop the stream before exiting.",
            )
            return  # Prevent closing
        self.root.destroy()  # Allow closing
