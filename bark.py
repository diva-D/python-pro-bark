import os
import commands
from typing import Any, Union, Callable, cast
from pydantic_types import ResponseGithubStars

class Option:
    def __init__(self, name: str, command: commands.Command, prep_call: Union[None, Callable[..., Any]] = None) -> None:
        self.name = name
        self.command = command
        self.prep_call = prep_call
        
    def choose(self) -> None:
        data = self.prep_call() if self.prep_call else None
        message: str = self.command.execute(data) if data else self.command.execute()  # type: ignore
        print(message)
        
    def __str__(self):
        return self.name

def print_options(options: dict[str, Option]) -> None:
    for shortcut, option in options.items():
        print(f"({shortcut}) {option}")
        
def get_user_choice(options: dict[str, Option]) -> Option:  # type: ignore
    valid_choice = False
    while not valid_choice:
        user_choice: str = input("Enter choice: ").upper()
        if options.get(user_choice):
            return options[user_choice]


def get_user_input(label: str, required: bool = True) -> Union[str, None]:
    value = input(f"{label}: ") or None
    while required and not value:
        value = input(f"{label}: ") or None
    return value

def get_new_bookmark_data() -> dict[str, Union[str, None]]:
    return {
        "title": get_user_input("Title"),
        "url": get_user_input("URL"),
        "notes": get_user_input("Notes", required=False),
    }

def get_delete_bookmark_data() -> str:
    return cast(str, get_user_input("Enter ID of bookmark to delete", required=True))


def get_github_stars_data() -> ResponseGithubStars:
    username = input("Github username: ")
    preserve_timestamps_input = input("Preserve timestamps [Y/n]: ")
    preserve_timestamps = preserve_timestamps_input.lower() == "y"
    return ResponseGithubStars(username=username, preserve_timestamps=preserve_timestamps)

def clear_screen():
    clear = 'cls' if os.name == 'nt' else 'clear'
    os.system(clear)


def loop():
    options: dict[str, Option] = {
        "A": Option("Add a bookmark", commands.AddBookmarkCommand(), cast(Callable[..., Any], get_new_bookmark_data)),
        "B": Option("List bookmarks by date", commands.ListBookmarksCommand(order_by="title")),
        "T": Option("List bookmarks by title", commands.ListBookmarksCommand(order_by="date_added")),
        "D": Option("Delete a bookmark", commands.DeleteBookmarkCommand(), cast(Callable[..., str], get_delete_bookmark_data)),
        "G": Option("Import Github stars", commands.ImportGithubStarsCommand(), cast(Callable[..., Any], get_github_stars_data)),
        "Q": Option("Quit", commands.QuitCommand())
    }
    print_options(options)
    print("")
    choice: Option = get_user_choice(options)
    print("")
    choice.choose()
    print("")
    _ = input('Press ENTER to return to menu')
    clear_screen()

    
if __name__ == "__main__":
    commands.CreateBookmarksTableCommand().execute()
    while True:
        loop()