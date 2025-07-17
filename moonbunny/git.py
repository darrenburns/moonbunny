import asyncio
from typing import Tuple, Type, Any


class AsyncGitShell:
    def __init__(self, working_dir: str):
        self.working_dir: str = working_dir
        self.marker: str = "---MOONBUNNY_GIT_SHELL_CMD_DONE---"
        self.process: asyncio.subprocess.Process | None = None

    async def __aenter__(self) -> "AsyncGitShell":
        self.process = await asyncio.create_subprocess_shell(
            "/bin/bash",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.working_dir,
        )
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        if self.process and self.process.returncode is None:
            try:
                self.process.terminate()
                await self.process.wait()
                print("\n✅ Moonbunny git shell closed.")
            except ProcessLookupError:
                pass

    async def run_command(self, command: str) -> Tuple[str, str]:
        full_command = f"{command}; echo {self.marker}; echo {self.marker} >&2\n"
        print(f"▶️ Moonbunny git shell: {command}")
        if (
            self.process is None
            or self.process.stdin is None
            or self.process.stdout is None
            or self.process.stderr is None
        ):
            raise RuntimeError("Process or its streams are not initialized.")
        self.process.stdin.write(full_command.encode("utf-8"))
        await self.process.stdin.drain()
        stdout_task = asyncio.create_task(self._read_stream(self.process.stdout))
        stderr_task = asyncio.create_task(self._read_stream(self.process.stderr))
        stdout_output, stderr_output = await asyncio.gather(stdout_task, stderr_task)
        return stdout_output, stderr_output

    async def _read_stream(self, stream: asyncio.StreamReader) -> str:
        output: list[str] = []
        while True:
            line_bytes = await stream.readline()
            if not line_bytes:
                break
            line = line_bytes.decode("utf-8")
            if self.marker in line:
                break
            output.append(line)
        return "".join(output)
