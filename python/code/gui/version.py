import sys
from pathlib import Path


def read_version():
    """Read version from VERSION file"""
    try:
        if getattr(sys, "frozen", False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).resolve().parent.parent.parent
        version_file = base_path / "VERSION"
        return version_file.read_text().strip()
    except Exception:
        return "unknown"
