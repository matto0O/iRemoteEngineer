import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
import os
import json
import requests

logger = logging.getLogger(__name__)

FEEDBACK_TYPES = [
    ("Bug Report", "bug_report"),
    ("Feature Request", "feature_request"),
    ("Inquiry", "inquiry"),
]


def get_feedback_tab(notebook, log_text_widget):
    """
    Creates and returns the feedback tab frame.

    Args:
        notebook: The parent ttk.Notebook widget
        log_text_widget: The ScrolledText widget from the Logs tab to grab log content

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
            frame, log_text_widget, type_combo, email_entry,
            topic_entry, description_text, submit_btn,
        ),
    )
    submit_btn.pack(anchor=tk.E)

    return frame


def _get_type_value(display_text):
    for label, value in FEEDBACK_TYPES:
        if label == display_text:
            return value
    return None


def _submit(frame, log_text_widget, type_combo, email_entry,
            topic_entry, description_text, submit_btn):
    feedback_type = _get_type_value(type_combo.get())
    topic = topic_entry.get().strip()
    description = description_text.get("1.0", tk.END).strip()

    if not feedback_type or not topic or not description:
        messagebox.showwarning("Missing fields", "Please fill in Type, Topic, and Description.")
        return

    email = email_entry.get().strip() or None

    # Grab logs from the log widget
    logs = log_text_widget.get("1.0", tk.END).strip()

    url = os.getenv("FEEDBACK_URL")
    if not url:
        messagebox.showerror("Configuration Error", "FEEDBACK_URL is not set in .env")
        return

    payload = {
        "type": feedback_type,
        "email": email,
        "title": topic,
        "description": description,
        "logs": logs,
    }

    submit_btn.configure(state="disabled", text="Submitting...")

    def do_request():
        try:
            response = requests.post(
                url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=15,
            )

            if response.status_code != 200:
                raise Exception(f"Server returned status {response.status_code}: {response.text}")

            data = response.json()
            issue_id = data.get("issue_id", "unknown")

            frame.after(0, lambda: _on_success(
                frame, issue_id, type_combo, email_entry,
                topic_entry, description_text, submit_btn,
            ))

        except Exception as e:
            logger.error(f"Feedback submission failed: {e}")
            frame.after(0, lambda: _on_error(frame, submit_btn, str(e)))

    threading.Thread(target=do_request, daemon=True).start()


def _on_success(frame, issue_id, type_combo, email_entry,
                topic_entry, description_text, submit_btn):
    submit_btn.configure(state="normal", text="Submit Feedback")

    # Clear form
    type_combo.set("")
    email_entry.delete(0, tk.END)
    topic_entry.delete(0, tk.END)
    description_text.delete("1.0", tk.END)

    messagebox.showinfo("Feedback Submitted", f"Issue created: #{issue_id}")


def _on_error(frame, submit_btn, error_msg):
    submit_btn.configure(state="normal", text="Submit Feedback")
    messagebox.showerror("Submission Failed", f"Could not submit feedback.\n\n{error_msg}")
