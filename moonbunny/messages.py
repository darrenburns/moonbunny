from dataclasses import dataclass, field
import shlex
from typing import Self

from rich.repr import Result
from textual.message import Message


@dataclass
class GitCommand(Message):
    """Request to run a git command."""

    command_name: str
    """The name of the git command to run e.g. 'status', 'add', 'commit', etc."""

    _args: list[str] = field(init=False, default_factory=list)

    @classmethod
    def with_args(cls, command_name: str, *args: str) -> Self:
        instance = cls(command_name)
        instance._args = [shlex.quote(arg) for arg in args]
        return instance

    @property
    def command(self) -> list[str]:
        return ["git", self.command_name] + self._args

    def __rich_repr__(self):
        yield "command_name", self.command_name
        yield "args", self._args


@dataclass
class GitCommandResult(Message):
    """Result of a git command."""

    command_number: int
    """The number of the command.

    A monotonically increasing sequence number assigned to each command by the app.
    """

    command: GitCommand
    """The command that was run."""

    stdout: bytes
    """The stdout of the command."""

    stderr: bytes
    """The stderr of the command."""

    returncode: int | None
    """The return code of the command."""

    def __rich_repr__(self):
        yield "command_number", self.command_number
        yield "command", self.command
        yield "stdout", self.stdout
        yield "stderr", self.stderr
        yield "returncode", self.returncode
