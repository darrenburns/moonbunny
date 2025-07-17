import asyncio
import shlex

from textual import log
from textual.app import App

from moonbunny.messages import GitCommand, GitCommandResult


class GitRunner:
    def __init__(self, mb: App[None]):
        self.mb: App[None] = mb
        self.task: asyncio.Task[None] | None = None
        self.commands: asyncio.Queue[tuple[int, GitCommand]] = asyncio.Queue()

    async def start(self) -> None:
        self.task = asyncio.create_task(self._run_loop())

    async def _run_loop(self) -> None:
        while True:
            command_number, command = await self.commands.get()
            stdout, stderr, returncode = await self._run_command(command)

            # Send the result back to the app.
            self.mb.post_message(
                GitCommandResult(
                    command_number=command_number,
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
