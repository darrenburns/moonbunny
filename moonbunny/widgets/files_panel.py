from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class FilesPanel(Vertical):
    """A panel for displaying files."""

    def compose(self) -> ComposeResult:
        yield OptionList("Files")

    def set_files(self, files: list[str]) -> None:
        """Set the files to display."""

        # Check the currently highlighted option ID, so that if it's still present after
        # the list is updated, we can re-highlight it.
        option_list = self.query_one(OptionList)
        highlighted_index = option_list.highlighted or 0
        previous_highlighted_option_id = option_list.options[highlighted_index].id

        # Clear the list and add the new files.
        option_list.clear_options()
        option_list.add_options([Option(file, id=file) for file in files])

        # Re-highlight the previously highlighted option, if it's still present.
        for index, option in enumerate(option_list.options):
            if option.id == previous_highlighted_option_id:
                option_list.highlighted = index
                break
        else:
            option_list.highlighted = 0
