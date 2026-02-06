import tkinter as tk
from tkinter import ttk
import threading
import logging
import os
import json
import requests

from gui.data_settings_tab import load_intervals
from gui.pit_stop_settings_tab import load_pit_settings
from gui.gui_utils import read_version

logger = logging.getLogger(__name__)

FEEDBACK_TYPES = [
    ("Bug Report", "bug_report"),
    ("Feature Request", "feature_request"),
    ("Inquiry", "inquiry"),
]


def get_feedback_tab(notebook, log_text_widget, status_bar):
    """
    Creates and returns the feedback tab frame.

    Args:
        notebook: The parent ttk.Notebook widget
        log_text_widget: The ScrolledText widget from the Logs tab to grab log content
        status_bar: The StatusBar widget for displaying status messages

    Returns:
        ttk.Frame: The configured feedback tab frame
    """
    frame = ttk.Frame(notebook)

    container = ttk.Frame(frame, padding=15)
    container.pack(fill=tk.BOTH, expand=True)

    # Type
    ttk.Label(container, text="Type").pack(anchor=tk.W)
    type_display_values = [label for label, _ in FEEDBACK_TYPES]
    type_combo = ttk.Combobox(
        container, values=type_display_values, state="readonly", width=40
    )
    type_combo.pack(fill=tk.X, pady=(0, 10))

    # Email (optional)
    ttk.Label(container, text="Email (optional)").pack(anchor=tk.W)
    email_entry = ttk.Entry(container, width=40)
    email_entry.pack(fill=tk.X, pady=(0, 10))

    # Topic
    ttk.Label(container, text="Topic").pack(anchor=tk.W)
    topic_entry = ttk.Entry(container, width=40)
    topic_entry.pack(fill=tk.X, pady=(0, 10))

    # Description
    ttk.Label(container, text="Description").pack(anchor=tk.W)
    description_text = tk.Text(container, height=6, wrap=tk.WORD)
    description_text.pack(fill=tk.X, pady=(0, 10))

    # Submit button
    submit_btn = ttk.Button(
        container,
        text="Submit Feedback",
        command=lambda: _submit(
            frame,
            log_text_widget,
            status_bar,
            type_combo,
            email_entry,
            topic_entry,
            description_text,
            submit_btn,
        ),
    )
    submit_btn.pack(anchor=tk.E)

    return frame


def _get_type_value(display_text):
    for label, value in FEEDBACK_TYPES:
        if label == display_text:
            return value
    return None


def _submit(
    frame,
    log_text_widget,
    status_bar,
    type_combo,
    email_entry,
    topic_entry,
    description_text,
    submit_btn,
):
    feedback_type = _get_type_value(type_combo.get())
    topic = topic_entry.get().strip()
    description = description_text.get("1.0", tk.END).strip()

    if not feedback_type or not topic or not description:
        status_bar.set_status("Please fill in Type, Topic, and Description", "error")
        return

    email = email_entry.get().strip() or None

    # Prepend settings to logs
    settings_lines = [f"=== App v{read_version()} ==="]
    try:
        pit = load_pit_settings()
        settings_lines.append("Pit Stop Settings:")
        for key, val in pit.items():
            settings_lines.append(f"  {key}: {val}")
    except Exception:
        settings_lines.append("Pit Stop Settings: (failed to load)")

    try:
        data = load_intervals()
        settings_lines.append("Data Settings:")
        for key, val in data.items():
            settings_lines.append(f"  {key}: {val}")
    except Exception:
        settings_lines.append("Data Settings: (failed to load)")

    settings_lines.append("================\n")
    settings_block = "\n".join(settings_lines)

    # Grab logs from the log widget
    logs = settings_block + log_text_widget.get("1.0", tk.END).strip()

    url = os.getenv("FEEDBACK_URL")
    if not url:
        status_bar.set_status("FEEDBACK_URL is not configured", "error")
        return

    payload = {
        "type": feedback_type,
        "email": email,
        "title": topic,
        "description": description,
        "logs": logs,
    }

    submit_btn.configure(state="disabled", text="Submitting...")
    status_bar.set_status("Submitting feedback...", "loading")

    def do_request():
        try:
            response = requests.post(
                url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=15,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Server returned status {response.status_code}: {response.text}"
                )

            data = response.json()
            issue_id = data.get("issue_id", "unknown")

            frame.after(
                0,
                lambda: _on_success(
                    frame,
                    issue_id,
                    status_bar,
                    type_combo,
                    email_entry,
                    topic_entry,
                    description_text,
                    submit_btn,
                ),
            )

        except Exception as e:
            logger.error(f"Feedback submission failed: {e}")
            frame.after(0, lambda: _on_error(status_bar, submit_btn, str(e)))

    threading.Thread(target=do_request, daemon=True).start()


def _on_success(
    frame,
    issue_id,
    status_bar,
    type_combo,
    email_entry,
    topic_entry,
    description_text,
    submit_btn,
):
    submit_btn.configure(state="normal", text="Submit Feedback")
    status_bar.clear()

    # Clear form
    type_combo.set("")
    email_entry.delete(0, tk.END)
    topic_entry.delete(0, tk.END)
    description_text.delete("1.0", tk.END)

    # Show custom dialog with Copy Issue ID + OK buttons
    root = frame.winfo_toplevel()
    dialog = tk.Toplevel(root)
    dialog.title("Feedback Submitted")
    dialog.resizable(False, False)
    dialog.transient(root)

    # Center dialog over the main window
    dw, dh = 350, 130
    root.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() - dw) // 2
    y = root.winfo_y() + (root.winfo_height() - dh) // 2
    dialog.geometry(f"{dw}x{dh}+{x}+{y}")

    dialog.grab_set()

    ttk.Label(
        dialog,
        text=f"Feedback submitted!\nIssue ID: #{issue_id}",
        font=("Helvetica", 11),
        justify=tk.CENTER,
    ).pack(pady=(20, 15))

    btn_frame = ttk.Frame(dialog)
    btn_frame.pack(pady=(0, 10))

    def copy_issue_id():
        dialog.clipboard_clear()
        dialog.clipboard_append(f"#{issue_id}")
        status_bar.set_status("Issue ID copied to clipboard", "success")

    ttk.Button(
        btn_frame,
        text="Copy Issue ID",
        command=copy_issue_id,
        width=15,
    ).pack(side=tk.LEFT, padx=(0, 10))

    ttk.Button(
        btn_frame,
        text="OK",
        command=dialog.destroy,
        width=10,
    ).pack(side=tk.LEFT)


def _on_error(status_bar, submit_btn, error_msg):
    submit_btn.configure(state="normal", text="Submit Feedback")
    status_bar.set_status(f"Feedback submission failed: {error_msg}", "error")
