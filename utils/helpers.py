"""
General helper utilities.
"""

import os
import re


def sanitize_filename(name: str) -> str:
    """Convert a string to a safe filesystem filename."""
    return re.sub(r"[^\w\-_]", "_", name).lower()


def ensure_dir(path: str):
    """Create directory (and parents) if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def format_prompt(template: str, **kwargs) -> str:
    return template.format(**kwargs)
