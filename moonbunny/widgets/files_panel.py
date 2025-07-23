from pathlib import Path
from textual import getters
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class FilesPanel(Vertical):
    """A panel for displaying files."""

    option_list = getters.child_by_id("files-panel-option-list", OptionList)

    def compose(self) -> ComposeResult:
        self.add_class("panel")
        self.border_title = "[u]F[/u]iles"
        yield OptionList(id="files-panel-option-list", markup=False, compact=True)

    def set_files(self, files: list[str]) -> None:
        """Set the files to display."""

        # Check the currently highlighted option ID, so that if it's still present after
        # the list is updated, we can re-highlight it.
        option_list = self.option_list
        highlighted_index = option_list.highlighted or 0
        if option_list.option_count == 0:
            previous_highlighted_option_id = None
        else:
            previous_highlighted_option_id = option_list.options[highlighted_index].id

        # Clear the list and add the new files.
        option_list.clear_options()
        option_list.add_options(
            [Option(Path(file).name, id=file) for file in files if file]
        )

        # Re-highlight the previously highlighted option, if it's still present.
        for index, option in enumerate(option_list.options):
            if option.id == previous_highlighted_option_id:
                option_list.highlighted = index
                break
        else:
            option_list.highlighted = 0
