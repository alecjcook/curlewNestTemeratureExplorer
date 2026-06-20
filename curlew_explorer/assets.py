from pathlib import Path
import sys


def get_base_path():
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "assets" / "frame0"
    return Path(__file__).resolve().parent.parent / "assets" / "frame0"


ASSETS_PATH = get_base_path()


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

