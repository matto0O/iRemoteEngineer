import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import threading
import logging
import os

from gui.streaming_lifecycle import (
    create_lobby_and_stream,
    join_lobby_and_stream,
    StreamingThreadController,
)
from gui.pit_stop_settings_tab import load_pit_settings

logger = logging.getLogger(__name__)


def get_streaming_tab(notebook, debug=False):
    """
    Creates and returns the streaming tab frame with lobby creation/joining functionality.

    Args:
        notebook: The parent ttk.Notebook widget

    Returns:
        ttk.Frame: The configured streaming tab frame
    """
    frame = ttk.Frame(notebook)

    # Main container with padding
    main_container = ttk.Frame(frame, padding="20")
    main_container.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(
        main_container,
        text="iRemoteEngineer - Data Streaming",
        font=("Helvetica", 16, "bold"),
    )
    title_label.pack(pady=(0, 20))

    # ===== Mode Selection =====
    mode_frame = ttk.LabelFrame(main_container, text="Action", padding="10")
    mode_frame.pack(fill=tk.X, pady=(0, 15))

    mode_var = tk.StringVar(value="create")

    create_radio = ttk.Radiobutton(
        mode_frame, text="Create New Lobby", variable=mode_var, value="create"
    )
    create_radio.pack(anchor=tk.W, pady=2)

    join_radio = ttk.Radiobutton(
        mode_frame, text="Stream to Existing Lobby", variable=mode_var, value="join"
    )
    join_radio.pack(anchor=tk.W, pady=2)

    # ===== Lobby Configuration =====
    config_frame = ttk.LabelFrame(
        main_container, text="Lobby Configuration", padding="10"
    )
    config_frame.pack(fill=tk.X, pady=(0, 15))

    # Lobby Name
    lobby_name_label = ttk.Label(config_frame, text="Lobby Name:")
    lobby_name_label.grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))

    lobby_name_entry = ttk.Entry(config_frame, width=30)
    lobby_name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)

    # Passcode
    passcode_label = ttk.Label(config_frame, text="Passcode:")
    passcode_label.grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))

    passcode_entry = ttk.Entry(config_frame, width=30, show="*")
    passcode_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)

    # Make the entry column expand
    config_frame.columnconfigure(1, weight=1)

    # ===== Action Buttons =====
    button_frame = ttk.Frame(main_container)
    button_frame.pack(fill=tk.X, pady=(0, 15))

    def toggle_buttons(start_enabled: bool):
        """Enable or disable start/stop buttons based on streaming state"""
        if start_enabled:
            start_button.config(state=tk.NORMAL)
            stop_button.config(state=tk.DISABLED)
            lobby_name_entry.config(state=tk.NORMAL)
            passcode_entry.config(state=tk.NORMAL)
            create_radio.config(state=tk.NORMAL)
            join_radio.config(state=tk.NORMAL)
        else:
            start_button.config(state=tk.DISABLED)
            stop_button.config(state=tk.NORMAL)
            lobby_name_entry.config(state=tk.DISABLED)
            passcode_entry.config(state=tk.DISABLED)
            create_radio.config(state=tk.DISABLED)
            join_radio.config(state=tk.DISABLED)

    def start_streaming_thread(lobby_name, passcode, mode):
        """Run the streaming initialization in a separate thread"""
        test_file = r"python\newdataset\data100.bin" if debug else None

        try:
            pit_stop_settings = load_pit_settings()
            if mode == "create":
                create_lobby_and_stream(
                    lobby_name, passcode, pit_stop_settings, test_file=test_file
                )
                message = f"Lobby created successfully!\n\nLobby Name: {lobby_name}\nPasscode: {passcode}\n\nShare the passcode with others to join."
            else:
                join_lobby_and_stream(
                    lobby_name, passcode, pit_stop_settings, test_file=test_file
                )
                message = f"Successfully joined lobby!\n\nLobby Name: {lobby_name}\nPasscode: {passcode}"

            # Use frame.after to safely show messagebox from background thread
            frame.after(0, lambda: messagebox.showinfo("Streaming Started", message))

        except Exception as e:
            # Show error dialog
            logger.error(f"Failed to start streaming: {e}", exc_info=True)
            frame.after(
                0,
                lambda error=e: messagebox.showerror(
                    "Error", f"Failed to start streaming:\n{str(error)}"
                ),
            )
            # Re-enable buttons on error
            frame.after(0, lambda: toggle_buttons(start_enabled=True))

    def handle_start():
        """Handle the start button click"""
        lobby_name = lobby_name_entry.get().strip()
        passcode = passcode_entry.get().strip()
        mode = mode_var.get()

        # Validation
        if not lobby_name:
            messagebox.showerror("Error", "Please enter a lobby name")
            return

        if not passcode:
            messagebox.showerror("Error", "Please enter a passcode")
            return

        if mode == "create":
            # Create new lobby
            messagebox.showinfo(
                "Creating Lobby",
                f"Creating lobby: {lobby_name}\n\nPlease wait while connecting to iRacing...",
            )
        else:
            # Join existing lobby
            messagebox.showinfo(
                "Joining Lobby",
                f"Joining lobby: {lobby_name}\n\nPlease wait while connecting to iRacing...",
            )

        # Disable buttons immediately
        toggle_buttons(start_enabled=False)

        # Start streaming in a background thread to avoid freezing UI
        streaming_thread = threading.Thread(
            target=start_streaming_thread,
            args=(lobby_name, passcode, mode),
            daemon=True,
        )
        streaming_thread.start()

    def stop_streaming_thread():
        """Stop streaming in a separate thread"""
        try:
            # Show immediate feedback
            frame.after(
                0,
                lambda: messagebox.showinfo(
                    "Stopping", "Stopping streaming, please wait..."
                ),
            )

            # Call stop with timeout built-in
            StreamingThreadController.stop_all_threads()

            # Always re-enable buttons after stop attempt (with or without timeout)
            frame.after(
                0, lambda: messagebox.showinfo("Streaming Stopped", "Streaming stopped")
            )
            frame.after(0, lambda: toggle_buttons(start_enabled=True))

        except Exception as e:
            frame.after(
                0,
                lambda: messagebox.showerror(
                    "Error", f"Error stopping stream:\n{str(e)}"
                ),
            )
            # Still re-enable buttons even on error
            frame.after(0, lambda: toggle_buttons(start_enabled=True))

    def handle_stop():
        """Handle the stop button click"""
        # Immediately disable stop button to prevent double-clicks
        stop_button.config(state=tk.DISABLED)

        # Stop in background thread to avoid freezing
        stop_thread = threading.Thread(target=stop_streaming_thread, daemon=True)
        stop_thread.start()

    start_button = ttk.Button(
        button_frame, text="Start Streaming", command=handle_start, width=20
    )
    start_button.pack(side=tk.LEFT, padx=(0, 10))

    stop_button = ttk.Button(
        button_frame,
        text="Stop Streaming",
        command=handle_stop,
        width=20,
        state=tk.DISABLED,  # Initially disabled until streaming starts
    )
    stop_button.pack(side=tk.LEFT)

    # ===== Web Interface Link =====
    web_frame = ttk.Frame(main_container)
    web_frame.pack(fill=tk.X, pady=(10, 0))

    def open_web_interface():
        """Open the web interface in the default browser"""
        url = os.getenv("WEBSITE_URL")
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser: {str(e)}")

    web_button = ttk.Button(
        web_frame, text="Open Web Interface", command=open_web_interface, width=25
    )
    web_button.pack(pady=5)

    return frame


def is_streaming():
    """Check if streaming is currently active"""
    return StreamingThreadController.are_threads_running()
