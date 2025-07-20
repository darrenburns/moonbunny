from pathlib import Path
from typing import Any
from textual import getters, on, log, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer

from moonbunny.git import (
    GitCommandResult,
    GitRequestAllFileDiffs,
    GitRequestCurrentBranchName,
    GitRequestFileStatus,
    GitTaskRunner,
)
from moonbunny.messages import GitCommand
from moonbunny.settings import Settings
from moonbunny.widgets.diff_panel import DiffPanel
from moonbunny.widgets.files_panel import FilesPanel
from moonbunny.widgets.status_bar import StatusBar


class Home(Screen[None]):
    BINDINGS = [
        Binding(key="s", action="git_status", description="status"),
        Binding(key="b", action="check_branch", description="branch"),
        Binding(key="d", action="check_all_file_diffs", description="diff all"),
    ]

    files_panel = getters.child_by_id("files-panel", FilesPanel)
    status_bar = getters.child_by_id("status-bar", StatusBar)
    diff_panel = getters.child_by_id("diff-panel", DiffPanel)

    def __init__(self, git: GitTaskRunner, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.git = git

    def compose(self) -> ComposeResult:
        yield StatusBar(id="status-bar")
        yield FilesPanel(id="files-panel")
        yield DiffPanel(id="diff-panel")
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        self.git.enqueue_request_file_status()
        self.git.enqueue_request_branch_name()
        self.git.enqueue_request_all_file_diffs()

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

    ALLOW_SELECT = False
    CSS_PATH = Path(__file__).parent / "moonbunny.scss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
    ]

    settings: Settings
    git: GitTaskRunner

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.git = GitTaskRunner(self)

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
        log.debug(result)
        log.debug(result.command.command_name)

        # Depending on the original command, handle the result differently.
        match result.command:
            case GitRequestFileStatus():
                output = result.stdout.decode("utf-8")
                lines = output.splitlines()
                lines = [line.split()[-1] for line in lines if line]
                self.home_screen.files_panel.set_files(lines)
            case GitRequestCurrentBranchName():
                branch_name = result.stdout.decode("utf-8").strip()
                self.home_screen.status_bar.set_branch_name(branch_name)
            case GitRequestAllFileDiffs():
                output = result.stdout.decode("utf-8")
                self.home_screen.diff_panel.set_diff(output)
            case _:
                log.warning(f"Unknown git command: {result.command}")

    @work(exclusive=True, group="git-watcher")
    async def watch_git_files(self) -> None:
        """Watching git files."""

        from watchfiles import awatch  # type: ignore

        async for changes in awatch(Path.cwd()):  # type: ignore
            for change_type, file_path in changes:  # type: ignore
                log.debug(f"Git file changed: {file_path}")


def main() -> None:
    app = Moonbunny()
    app.settings = Settings()
    app.run()


if __name__ == "__main__":
    main()
