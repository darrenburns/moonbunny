from textual import getters
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.content import Content
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class BranchesPanel(Vertical):
    option_list = getters.child_by_id("branches-panel-option-list", OptionList)

    def compose(self) -> ComposeResult:
        self.add_class("panel")
        self.border_title = "[u]B[/u]ranches"
        yield OptionList(id="branches-panel-option-list", compact=True)

    def set_branches(self, branches: list[str]) -> None:
        option_list = self.option_list
        option_list.clear_options()

        options: list[Option] = []
        for branch_entry in branches:
            # Check if the branch entry has the time format "Xm branch-name" or "Xh branch-name" etc.
            parts = branch_entry.split(" ", 1)
            if (
                len(parts) == 2
                and any(
                    parts[0].endswith(suffix)
                    for suffix in ["m", "h", "d", "w", "mo", "y"]
                )
                or parts[0] == "now"
            ):
                # Extract just the branch name for the ID
                branch_name = parts[1]
                # Display the full format with time
                display_text = Content.assemble(
                    (parts[0], "$text-accent on $accent-muted 30%"),
                    " ",
                    branch_name,
                )
            else:
                # Fallback: use the entire entry as both display and ID
                branch_name = branch_entry
                display_text = branch_entry

            options.append(Option(display_text, id=branch_name))

        option_list.add_options(options)
