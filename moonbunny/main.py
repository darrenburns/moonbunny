from pathlib import Path
from typing import Any
from textual import getters, on, log, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Label

from moonbunny.git import (
    GitCommandResult,
    GitRequestAllFileDiffs,
    GitRequestCommits,
    GitRequestCurrentBranchName,
    GitRequestFileStatus,
    GitRequestRecentBranches,
    GitTaskRunner,
    format_relative_time,
)
from moonbunny.messages import GitCommand
from moonbunny.models import FileStatus
from moonbunny.settings import Settings
from moonbunny.widgets.branches_panel import BranchesPanel
from moonbunny.widgets.commits_panel import CommitsPanel
from moonbunny.widgets.diff_panel import DiffPanel
from moonbunny.widgets.files_panel import FilesPanel
from moonbunny.widgets.status_bar import StatusBar


class Home(Screen[None]):
    BINDINGS = [
        Binding(
            key="f",
            action="app.focus('files-panel-option-list')",
            description="focus files",
        ),
        Binding(
            key="b",
            action="app.focus('branches-panel-option-list')",
            description="focus branches",
        ),
        Binding(
            key="c",
            action="app.focus('commits-panel-option-list')",
            description="focus commits",
        ),
    ]

    files_panel = getters.query_one("#sidebar #files-panel", FilesPanel)
    status_bar = getters.child_by_id("status-bar", StatusBar)
    diff_panel = getters.query_one("#diff-panel", DiffPanel)
    branches_panel = getters.query_one("#sidebar #branches-panel", BranchesPanel)
    commits_panel = getters.query_one("#sidebar #commits-panel", CommitsPanel)

    def __init__(self, git: GitTaskRunner, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.git = git

    def compose(self) -> ComposeResult:
        yield StatusBar(id="status-bar")
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("moon[b]bunny 🐰 ", id="app-header")
                yield FilesPanel(id="files-panel")
                yield BranchesPanel(id="branches-panel")
                yield CommitsPanel(id="commits-panel")

            with Vertical(id="body"):
                yield Label("Diff", id="body-header")
                with VerticalScroll(id="body-panel-scroll"):
                    yield DiffPanel(id="diff-panel")
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        self.git.enqueue_request_file_status()
        self.git.enqueue_request_branch_name()
        self.git.enqueue_request_all_file_diffs()
        self.git.enqueue_recent_branches()
        self.git.enqueue_request_commits("HEAD")

    def action_git_status(self) -> None:
        self.git.enqueue_request_file_status()

    def action_check_branch(self) -> None:
        self.git.enqueue_request_branch_name()

    def action_check_all_file_diffs(self) -> None:
        self.git.enqueue_request_all_file_diffs()


class Moonbunny(App[None], inherit_bindings=False):
    """The main application. Contains global keybinds and config.

    Doesn't do any rendering - that's all done at the screen level.

    The app's message pump is also used to handle interaction with git.

    Send one of the messages prefixed with Git to this widget in order
    to handle git commands. This App will receive those messages and
    update the UI accordingly.
    """

    CSS_PATH = Path(__file__).parent / "moonbunny.scss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
    ]
    ALLOW_SELECT = False

    settings: Settings
    git: GitTaskRunner

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Initialize settings first so we can pass git_dir to GitTaskRunner
        self.theme = "tokyo-night"
        self.settings = Settings()
        self.git = GitTaskRunner(self, git_dir=self.settings.git_dir)

    async def on_ready(self) -> None:
        await self.git.start()
        self.watch_git_files()

    def get_default_screen(self) -> Screen[None]:
        self.home_screen = Home(self.git)
        return self.home_screen

    @on(GitCommand)
    def handle_git_command(self, command: GitCommand) -> None:
        self.git.commands.put_nowait(command)

    @on(GitCommandResult)
    def handle_git_command_result(self, result: GitCommandResult) -> None:
        log.debug(result.command.command_name)

        # Depending on the original command, handle the result differently.
        match result.command:
            case GitRequestFileStatus():
                output = result.stdout.decode("utf-8")
                log.debug(output)
                lines = output.splitlines()
                file_statuses: list[FileStatus] = []
                for line in lines:
                    if line.strip():
                        parts = line.split(maxsplit=8)
                        if len(parts) >= 9 and parts[0] == "1":
                            # Porcelain v2 format: 1 <XY> <sub> <mH> <mI> <mW> <hH> <hI> <path>
                            xy_status = parts[1]
                            path = Path(parts[8])
                            staged = xy_status[0] != "."  # X position - staged status
                            unstaged = (
                                xy_status[1] != "."
                            )  # Y position - unstaged status
                            status_char = xy_status
                            file_statuses.append(
                                FileStatus(path, staged, unstaged, status_char)
                            )
                        elif line.startswith("?"):
                            # Untracked files: ? <path>
                            path = Path(line[2:])  # Remove "? " prefix
                            file_statuses.append(FileStatus(path, False, True, "?"))
                self.home_screen.files_panel.set_files(file_statuses)
            case GitRequestCurrentBranchName():
                branch_name = result.stdout.decode("utf-8").strip()
                self.home_screen.status_bar.set_branch_name(branch_name)
            case GitRequestAllFileDiffs():
                output = result.stdout.decode("utf-8")
                self.home_screen.diff_panel.set_diff(output)
            case GitRequestRecentBranches():
                output = result.stdout.decode("utf-8")
                lines = output.splitlines()
                formatted_branches: list[str] = []
                for line in lines:
                    if "|" in line:
                        time_part, branch_name = line.split("|", 1)
                        formatted_time = format_relative_time(time_part.strip())
                        formatted_branches.append(f"{formatted_time} {branch_name}")
                    else:
                        # Fallback for branches without time info
                        formatted_branches.append(line)
                self.home_screen.branches_panel.set_branches(formatted_branches)
            case GitRequestCommits():
                output = result.stdout.decode("utf-8")
                lines = output.splitlines()
                # Filter out empty lines and set commits
                commits = [line for line in lines if line.strip()]
                self.home_screen.commits_panel.set_commits(commits)
            case _:
                log.warning(f"Unknown git command: {result.command}")

    @work(exclusive=True, group="git-watcher")
    async def watch_git_files(self) -> None:
        """Watching git files."""

        # Lazy import because it's slow and delays startup a decent amount.
        from watchfiles import awatch  # type: ignore

        async for changes in awatch(Path.cwd()):  # type: ignore
            for change_type, file_path in changes:  # type: ignore
                log.debug(f"Git file changed: {file_path}")


def main() -> None:
    app = Moonbunny()
    app.run()


if __name__ == "__main__":
    main()
