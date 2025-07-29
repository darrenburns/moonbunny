from pathlib import Path
from typing import NamedTuple


class FileStatus(NamedTuple):
    """Represents a file's git status information."""

    path: Path
    staged: bool
    unstaged: bool
    status_char: str  # The git status character (M, A, D, etc.)
