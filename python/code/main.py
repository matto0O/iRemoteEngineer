import sys
import os
from pathlib import Path
from dotenv import load_dotenv

from gui.gui_main import IracingDataGUI
import tkinter as tk

if getattr(sys, "frozen", False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = Path(__file__).parent.parent

env_path = os.path.join(bundle_dir, ".env")
load_dotenv(env_path)

if __name__ == "__main__":
    root = tk.Tk()
    gui = IracingDataGUI(root)
    root.mainloop()
