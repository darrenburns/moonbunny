from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widgets import Label


class StatusBar(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Label("")

    def set_branch_name(self, branch_name: str) -> None:
        self.query_one(Label).update(f"{branch_name}")
