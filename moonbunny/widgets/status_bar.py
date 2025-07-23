from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widgets import Label


class StatusBar(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Label("", id="status")
        with HorizontalGroup(id="repo-and-branch"):
            yield Label("", id="repo-name")
            yield Label("", id="branch-name")

    def set_branch_name(self, branch_name: str) -> None:
        self.query_one("#branch-name", Label).update(f"{branch_name}")

    def set_repo_name(self, repo_name: str) -> None:
        self.query_one("#repo-name", Label).update(f"{repo_name}")
