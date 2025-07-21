from textual import getters
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class CommitsPanel(Vertical):
    """A panel for displaying commits."""

    option_list = getters.child_by_id("commits-panel-option-list", OptionList)

    def compose(self) -> ComposeResult:
        self.add_class("panel")
        self.border_title = "[u]C[/u]ommits"
        yield OptionList(id="commits-panel-option-list", compact=True)

    def set_commits(self, commits: list[str]) -> None:
        """Set the commits to display."""

        # Check the currently highlighted option ID, so that if it's still present after
        # the list is updated, we can re-highlight it.
        option_list = self.option_list
        highlighted_index = option_list.highlighted or 0
        if option_list.option_count == 0:
            previous_highlighted_option_id = None
        else:
            previous_highlighted_option_id = option_list.options[highlighted_index].id

        # Clear the list and add the new commits.
        option_list.clear_options()

        options: list[Option] = []
        for commit in commits:
            if commit.strip():  # Skip empty lines
                # Parse commit format: "abc1234 Commit message"
                parts = commit.split(" ", 1)
                if len(parts) >= 2:
                    commit_hash = parts[0]
                    # Use full commit line as display text, hash as ID
                    options.append(Option(commit, id=commit_hash))
                else:
                    # Fallback for malformed commits
                    options.append(Option(commit, id=commit))

        option_list.add_options(options)

        # Re-highlight the previously highlighted option, if it's still present.
        for index, option in enumerate(option_list.options):
            if option.id == previous_highlighted_option_id:
                option_list.highlighted = index
                break
        else:
            option_list.highlighted = 0
