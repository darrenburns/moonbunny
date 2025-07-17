from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widgets import Label


class StatusBar(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Label("Status Bar")
