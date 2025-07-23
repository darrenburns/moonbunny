from textual import getters
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.content import Content
from textual.widgets import OptionList
from textual.widgets.option_list import Option


def _get_initials(author_name: str) -> str:
    """Generate initials from author name. E.g., 'Darren Burns' -> 'DB'"""
    words = author_name.strip().split()
    initials = "".join(word[0].upper() for word in words if word)
    return initials[:2]  # Limit to 2 characters max


def _get_author_colour(author_name: str) -> str:
    """Get a consistent colour for an author based on their name."""
    colours = [
        "$text-accent on $accent-muted 80%",
        "$text-secondary on $secondary-muted 80%",
        "$text-primary on $primary-muted 80%",
        "$text-success on $success-muted 80%",
        "$text-warning on $warning-muted 80%",
        "$text-error on $error-muted 80%",
    ]

    # Consistently map names to colours.
    author_hash = hash(author_name) % len(colours)
    return colours[author_hash]


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
                # Parse commit format: "abc1234|Author Name|Commit message"
                parts = commit.split("|")
                if len(parts) >= 3:
                    commit_hash, author_name, message = parts
                    initials = _get_initials(author_name)
                    author_colour = _get_author_colour(author_name)
                    # Use styled content with hash, initials, and message
                    options.append(
                        Option(
                            Content.assemble(
                                (
                                    f"{initials:>2}",
                                    f"{author_colour}",
                                ),
                                " ",
                                message,
                            ),
                            id=commit_hash,
                        )
                    )
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
