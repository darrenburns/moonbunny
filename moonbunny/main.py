from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer

from moonbunny.settings import Settings
from moonbunny.widgets.status_bar import StatusBar


class Moonbunny(App[None], inherit_bindings=False):
    ALLOW_SELECT = False
    CSS_PATH = Path(__file__).parent / "moonbunny.scss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
    ]

    settings: Settings

    def get_default_screen(self) -> Screen[None]:
        return Home()


class Home(Screen[None]):
    def compose(self) -> ComposeResult:
        yield StatusBar()
        yield Footer(show_command_palette=False)


def main() -> None:
    app = Moonbunny()
    app.settings = Settings()
    app.run()


if __name__ == "__main__":
    main()
