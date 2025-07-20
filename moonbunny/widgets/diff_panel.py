from typing import Any
from textual.content import Content
from textual.widgets import Static


class DiffPanel(Static):
    """A panel for displaying diffs."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs, markup=False)

    def set_diff(self, diff: str) -> None:
        diff_lines = diff.splitlines(keepends=True)
        coloured_diff: list[tuple[str, str]] = []
        for line in diff_lines:
            if line.startswith("+"):
                coloured_diff.append((line, "$text-success on $success-muted"))
            elif line.startswith("-"):
                coloured_diff.append((line, "$text-error on $error-muted"))
            else:
                coloured_diff.append((line, "$foreground"))

        content = Content.assemble(*coloured_diff)
        self.update(content)
