from textual import getters
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.content import Content
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from moonbunny.models import FileStatus


class FilesPanel(Vertical):
    """A panel for displaying files."""

    option_list = getters.child_by_id("files-panel-option-list", OptionList)

    def compose(self) -> ComposeResult:
        self.add_class("panel")
        self.border_title = "[u]F[/u]iles"
        yield OptionList(id="files-panel-option-list", markup=False, compact=True)

    def set_files(self, files: list[FileStatus]) -> None:
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

        # Create options for each file status
        options: list[Option] = []
        for file_status in files:
            # Create a display name that shows the status with proper styling
            option_id = str(file_status.path)

            if file_status.staged and file_status.unstaged:
                # Both staged and unstaged
                display_content = Content.assemble(
                    (" ✔️ ", "$text-success on $success-muted 30%"),
                    (" ✗ ", "$text-error on $error-muted 30%"),
                    " ",
                    file_status.path.name,
                )
            elif file_status.staged:
                # Staged only
                display_content = Content.assemble(
                    (" ✔️ ", "$text-success on $success-muted 30%"),
                    " ",
                    file_status.path.name,
                )
            elif file_status.unstaged:
                # Unstaged only
                display_content = Content.assemble(
                    (" ✗ ", "$text-error on $error-muted 30%"),
                    " ",
                    file_status.path.name,
                )
            else:
                # No status indicators (shouldn't happen with current logic)
                display_content = file_status.path.name

            options.append(Option(display_content, id=option_id))

        option_list.add_options(options)

        # Re-highlight the previously highlighted option, if it's still present.
        for index, option in enumerate(option_list.options):
            if option.id == previous_highlighted_option_id:
                option_list.highlighted = index
                break
        else:
            option_list.highlighted = 0
