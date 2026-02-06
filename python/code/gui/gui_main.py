import tkinter as tk
from tkinter import ttk, scrolledtext
import logging
import threading
import webbrowser

import requests

from gui.streaming_tab import get_streaming_tab, is_streaming
from gui.data_settings_tab import get_data_settings_tab
from gui.pit_stop_settings_tab import get_pit_settings_tab
from gui.feedback_tab import get_feedback_tab
from gui.log_handler import GUILogHandler
from gui.gui_utils import read_version, get_base_path

RELEASES_URL = "https://github.com/matto0O/iRemoteEngineer/releases"


def _show_update_dialog(root, latest_version, mandatory):
    """Show an update dialog. Mandatory blocks usage until update/exit."""
    dialog = tk.Toplevel(root)
    dialog.title("Update Required" if mandatory else "Update Available")
    dialog.resizable(False, False)
    dialog.transient(root)

    # Center dialog over the main window
    dw, dh = 350, 150
    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() - dw) // 2
    y = root.winfo_y() + (root.winfo_height() - dh) // 2
    dialog.geometry(f"{dw}x{dh}+{x}+{y}")

    dialog.grab_set()

    if mandatory:
        msg = (
            f"A mandatory update is available (v{latest_version}).\n"
            "Please download the new version to continue."
        )
    else:
        msg = (
            f"A new version is available (v{latest_version}).\n"
            "You can continue or download the update."
        )

    ttk.Label(
        dialog,
        text=msg,
        font=("Helvetica", 11),
        justify=tk.CENTER,
    ).pack(pady=(20, 15))

    btn_frame = ttk.Frame(dialog)
    btn_frame.pack(pady=(0, 10))

    def open_releases():
        webbrowser.open(RELEASES_URL)

    ttk.Button(
        btn_frame,
        text="Get New Release",
        command=open_releases,
        width=16,
    ).pack(side=tk.LEFT, padx=(0, 10))

    if mandatory:
        dialog.protocol("WM_DELETE_WINDOW", root.destroy)
        ttk.Button(
            btn_frame,
            text="Exit",
            command=root.destroy,
            width=10,
        ).pack(side=tk.LEFT)
    else:
        ttk.Button(
            btn_frame,
            text="Dismiss",
            command=dialog.destroy,
            width=10,
        ).pack(side=tk.LEFT)


def _check_for_updates(root, local_version):
    """Fetch the latest GitHub release and compare against the local version."""
    try:
        resp = requests.get(
            "https://api.github.com/repos/matto0O/iRemoteEngineer/releases/latest",
            timeout=5,
        )
        resp.raise_for_status()
        tag = resp.json().get("tag_name", "").lstrip("v")

        remote = tuple(int(x) for x in tag.split("."))
        local = tuple(int(x) for x in local_version.split("."))

        if remote == local:
            return

        mandatory = remote[0] != local[0] or remote[1] != local[1]
        root.after(0, _show_update_dialog, root, tag, mandatory)
    except Exception:
        pass


class StatusBar(tk.Frame):
    """Footer status bar with version (left) and status messages (right)"""

    SPINNER_CHARS = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def __init__(self, parent, version):
        super().__init__(parent, relief=tk.SUNKEN, borderwidth=1)

        # Version label (left)
        self.version_label = tk.Label(
            self,
            text=f"v{version}",
            anchor=tk.W,
            padx=8,
            pady=2,
            font=("Helvetica", 9),
            fg="#555555",
        )
        self.version_label.pack(side=tk.LEFT)

        # Status label (right)
        self.status_label = tk.Label(
            self,
            text="",
            anchor=tk.E,
            padx=8,
            pady=2,
            font=("Helvetica", 9),
        )
        self.status_label.pack(side=tk.RIGHT)

        # Spinner label (right, before status text)
        self.spinner_label = tk.Label(
            self,
            text="",
            anchor=tk.E,
            pady=2,
            font=("Helvetica", 9),
        )
        self.spinner_label.pack(side=tk.RIGHT)

        self._state = None
        self._spinner_index = 0
        self._spinner_after_id = None
        self._clear_after_id = None

    def set_status(self, message, state="loading"):
        """Set status message with state: 'loading', 'success', or 'error'"""
        # Cancel any pending clear/spinner
        if self._spinner_after_id:
            self.after_cancel(self._spinner_after_id)
            self._spinner_after_id = None
        if self._clear_after_id:
            self.after_cancel(self._clear_after_id)
            self._clear_after_id = None

        self._state = state

        if state == "loading":
            self.spinner_label.config(text=self.SPINNER_CHARS[0], fg="#333333")
            self.status_label.config(text=message, fg="#333333")
            self._spinner_index = 0
            self._animate_spinner()
        elif state == "success":
            self.spinner_label.config(text="✔ ", fg="#2e7d32")
            self.status_label.config(text=message, fg="#2e7d32")
            self._clear_after_id = self.after(5000, self.clear)
        elif state == "error":
            self.spinner_label.config(text="✖ ", fg="#c62828")
            self.status_label.config(text=message, fg="#c62828")
            self._clear_after_id = self.after(8000, self.clear)

    def clear(self):
        """Clear the status display"""
        if self._spinner_after_id:
            self.after_cancel(self._spinner_after_id)
            self._spinner_after_id = None
        if self._clear_after_id:
            self.after_cancel(self._clear_after_id)
            self._clear_after_id = None
        self._state = None
        self.spinner_label.config(text="")
        self.status_label.config(text="")

    def _animate_spinner(self):
        """Animate the spinner character"""
        if self._state != "loading":
            return
        self._spinner_index = (self._spinner_index + 1) % len(self.SPINNER_CHARS)
        self.spinner_label.config(text=self.SPINNER_CHARS[self._spinner_index] + " ")
        self._spinner_after_id = self.after(100, self._animate_spinner)


class IracingDataGUI:
    def __init__(self, root, debug=False):
        self.debug = debug
        self.root = root
        icon_path = get_base_path() / "favicon.ico"
        if icon_path.exists():
            self.root.iconbitmap(default=str(icon_path))
        self.root.title("iRemoteEngineer")
        self.root.geometry("600x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Read version
        version = read_version()

        # Create status bar (pack at bottom first so it stays there)
        self.status_bar = StatusBar(self.root, version)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create notebook for sections
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Streaming tab
        self.streaming_frame = get_streaming_tab(
            self.notebook, self.status_bar, debug=self.debug
        )
        self.notebook.add(self.streaming_frame, text="Streaming")

        # Data Settings tab
        self.data_settings_frame = get_data_settings_tab(self.notebook, self.status_bar)
        self.notebook.add(self.data_settings_frame, text="Data Settings")

        # Pit-stop tab
        self.pit_settings_frame = get_pit_settings_tab(self.notebook, self.status_bar)
        self.notebook.add(self.pit_settings_frame, text="Pit Settings")

        # Logs tab
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Logs")
        self.log_text = scrolledtext.ScrolledText(
            self.logs_frame, wrap=tk.WORD, height=20, state="disabled"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Set up logging to GUI
        self.setup_logging()

        # Feedback tab (after logging setup so log_text is ready)
        self.feedback_frame = get_feedback_tab(
            self.notebook, self.log_text, self.status_bar
        )
        self.notebook.add(self.feedback_frame, text="Feedback")

        # Check for updates in background
        threading.Thread(
            target=_check_for_updates, args=(self.root, version), daemon=True
        ).start()

    def setup_logging(self):
        """Configure logging to write to the GUI log widget"""
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setLevel(logging.INFO)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.handlers.clear()
        root_logger.addHandler(gui_handler)

        logging.info("iRemoteEngineer logging initialized")

    def on_close(self):
        if is_streaming():
            self.status_bar.set_status(
                "Stop streaming before closing the application", "error"
            )
            return
        self.root.destroy()
