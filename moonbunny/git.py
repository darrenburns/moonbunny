import asyncio
import shlex
import re

from textual import log
from textual.app import App

from moonbunny.messages import GitCommand, GitCommandResult


def format_relative_time(relative_time: str) -> str:
    """Format git's relative time into a concise format.

    Examples:
        "2 minutes ago" -> "2m"
        "3 hours ago" -> "3h"
        "1 day ago" -> "1d"
        "2 weeks ago" -> "2w"
        "1 month ago" -> "1mo"
        "1 year ago" -> "1y"
    """
    # Handle "just now" case
    if "second" in relative_time or relative_time.strip() == "":
        return "now"

    # Extract number and unit
    match = re.search(r"(\d+)\s+(minute|hour|day|week|month|year)", relative_time)
    if not match:
        return relative_time  # Return original if no match

    number, unit = match.groups()

    # Map units to short forms
    unit_map = {
        "minute": "m",
        "hour": "h",
        "day": "d",
        "week": "w",
        "month": "mo",
        "year": "y",
    }

    short_unit = unit_map.get(unit, unit)
    return f"{number}{short_unit}"


class GitTaskRunner:
    def __init__(self, mb: App[None], git_dir: str | None = None):
        self.mb: App[None] = mb
        self.git_dir = git_dir
        self.task: asyncio.Task[None] | None = None
        self.commands: asyncio.Queue[GitCommand] = asyncio.Queue()

    async def start(self) -> None:
        self.task = asyncio.create_task(self._run_loop())

    async def _run_loop(self) -> None:
        while True:
            command = await self.commands.get()
            print(command)
            stdout, stderr, returncode = await self._run_command(command)

            # Send the result back to the app.
            self.mb.post_message(
                GitCommandResult(
                    command=command,
                    stdout=stdout,
                    stderr=stderr,
                    returncode=returncode,
                )
            )

            self.commands.task_done()

    async def _run_command(
        self, command: GitCommand
    ) -> tuple[bytes, bytes, int | None]:
        # Build the command, injecting -C option if git_dir is set
        cmd_parts = command.command.copy()
        if self.git_dir:
            # Insert -C option after 'git' but before the command name
            cmd_parts = ["git", "-C", self.git_dir] + cmd_parts[1:]

        run_command = shlex.join(cmd_parts)
        log.debug(f"Running command: {run_command}")
        process = await asyncio.create_subprocess_shell(
            run_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return stdout, stderr, process.returncode

    def enqueue_request_file_status(self) -> None:
        """Request the status of the files in the repository."""
        self.commands.put_nowait(GitRequestFileStatus())

    def enqueue_request_branch_name(self) -> None:
        """Request the name of the current branch."""
        self.commands.put_nowait(GitRequestCurrentBranchName())

    def enqueue_request_file_diff(self, file_path: str) -> None:
        """Request the diff of a file."""
        self.commands.put_nowait(GitRequestFileDiff(file_path))

    def enqueue_request_all_file_diffs(self) -> None:
        """Request the diff of all files in the repository."""
        self.commands.put_nowait(GitRequestAllFileDiffs())

    def enqueue_recent_branches(self) -> None:
        """Request the recent branches."""
        self.commands.put_nowait(GitRequestRecentBranches(requires_escape=False))

    def enqueue_request_commits(self, branch_name: str) -> None:
        """Request the commits for a branch."""
        self.commands.put_nowait(GitRequestCommits(branch_name))


class GitRequestFileStatus(GitCommand):
    def __init__(self) -> None:
        super().__init__("status", ["--porcelain=v2"])


class GitRequestCurrentBranchName(GitCommand):
    def __init__(self) -> None:
        super().__init__("rev-parse", ["--symbolic-full-name", "--abbrev-ref", "HEAD"])


class GitRequestFileDiff(GitCommand):
    def __init__(self, file_path: str) -> None:
        super().__init__("diff", ["--", file_path])


class GitRequestAllFileDiffs(GitCommand):
    def __init__(self) -> None:
        super().__init__("diff")


class GitRequestCommits(GitCommand):
    def __init__(self, branch_name: str) -> None:
        super().__init__(
            "log",
            ["--pretty=format:%h|%aN|%s", "-n", "200", branch_name],
            requires_escape=False,
        )


class GitRequestRecentBranches(GitCommand):
    def __init__(self, requires_escape: bool = True) -> None:
        super().__init__(
            "branch",
            [
                "--list",
                "--sort",
                "-committerdate",
                "--format",
                "%(committerdate:relative)|%(refname:short)",
            ],
            requires_escape=requires_escape,
        )
