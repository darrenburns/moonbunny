from dataclasses import dataclass, field
import shlex

from textual.message import Message


@dataclass
class GitCommand(Message):
    """Request to run a git command."""

    command_name: str
    """The name of the git command to run e.g. 'status', 'add', 'commit', etc."""

    args: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.args = [shlex.quote(arg) for arg in self.args]

    @property
    def command(self) -> list[str]:
        return ["git", self.command_name] + self.args

    def __rich_repr__(self):
        yield "command_name", self.command_name
        yield "args", self.args


@dataclass
class GitCommandResult(Message):
    """Result of a git command."""

    command: GitCommand
    """The command that was run."""

    stdout: bytes
    """The stdout of the command."""

    stderr: bytes
    """The stderr of the command."""

    returncode: int | None
    """The return code of the command."""

    def __rich_repr__(self):
        yield "command", self.command
        yield "stdout", self.stdout
        yield "stderr", self.stderr
        yield "returncode", self.returncode
