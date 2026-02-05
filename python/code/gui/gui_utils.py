import sys
from pathlib import Path


def get_base_path():
    """Return the project base path (python/ directory)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent.parent


def read_version():
    """Read version from VERSION file"""
    try:
        version_file = get_base_path() / "VERSION"
        return version_file.read_text().strip()
    except Exception:
        return "unknown"
