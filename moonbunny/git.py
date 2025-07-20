import asyncio
import shlex

from textual import log
from textual.app import App

from moonbunny.messages import GitCommand, GitCommandResult


class GitTaskRunner:
    def __init__(self, mb: App[None]):
        self.mb: App[None] = mb
        self.task: asyncio.Task[None] | None = None
        self.commands: asyncio.Queue[GitCommand] = asyncio.Queue()

    async def start(self) -> None:
        self.task = asyncio.create_task(self._run_loop())

    async def _run_loop(self) -> None:
        while True:
            command = await self.commands.get()
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
        run_command = shlex.join(command.command)
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


class GitRequestFileStatus(GitCommand):
    def __init__(self) -> None:
        super().__init__("status", ["--porcelain=v2"])


class GitRequestCurrentBranchName(GitCommand):
    def __init__(self) -> None:
        super().__init__("rev-parse", ["--symbolic-full-name", "--abbrev-ref", "HEAD"])
