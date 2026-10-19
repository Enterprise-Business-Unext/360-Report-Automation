import os
import sys

def resource_path(relative_path):
    """
    Returns absolute path to resource, works for both
    development and PyInstaller executable.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)