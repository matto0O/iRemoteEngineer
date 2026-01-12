import logging
import tkinter as tk

class GUILogHandler(logging.Handler):
    """Custom logging handler that writes to a tkinter ScrolledText widget"""

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                           datefmt='%H:%M:%S'))

    def emit(self, record):
        """Write log record to the GUI text widget"""
        try:
            msg = self.format(record)

            # Thread-safe GUI update
            def append():
                self.text_widget.configure(state='normal')
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.configure(state='disabled')
                # Auto-scroll to the bottom
                self.text_widget.see(tk.END)

            # Schedule the update on the main thread
            self.text_widget.after(0, append)
        except Exception:
            self.handleError(record)
