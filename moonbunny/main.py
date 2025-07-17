from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer


class Moonbunny(App[None], inherit_bindings=False):
    ALLOW_SELECT = False
    CSS_PATH = Path(__file__).parent / "moonbunny.scss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()


def main() -> None:
    app = Moonbunny()
    app.run()


if __name__ == "__main__":
    main()
