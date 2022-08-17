import os
import commands
from pprint import pprint
from typing import Any, Union, Callable, cast, Optional
from pydantic import BaseModel
from models.app import ResponseUpdateBookmark, ResponseGithubStars, ResponseCommand

class Option(BaseModel):
    name: str
    command: commands.Command
    prep_call: Optional[Callable[..., Any]] = None
    success_message: Optional[str] = "Success!"
        
    def choose(self) -> None:
        data = self.prep_call() if self.prep_call else None
        command_response: Optional[ResponseCommand] = self.command.execute(data)
        if command_response and command_response.status:
            if isinstance(command_response.result, list):
                pprint(command_response.result)
            elif self.success_message:
                print(self.success_message)
        elif command_response and command_response.error:
            print(command_response.error)
        
    def __str__(self):
        return self.name

def print_options(options: dict[str, Option]) -> None:
    for shortcut, option in options.items():
        print(f"({shortcut}) {option}")
        
def get_user_choice(options: dict[str, Option]) -> Optional[Option]:
    valid_choice = False
    while not valid_choice:
        user_choice: str = input("Enter choice: ").upper()
        if options.get(user_choice):
            return options[user_choice]
    return None

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

def get_update_bookmark_data() -> ResponseUpdateBookmark:
    return ResponseUpdateBookmark(
        id=input("ID of bookmark to update: "),
        column=input("Field to update: "),
        new_value=input("New value: ")
    )


def get_github_stars_data() -> ResponseGithubStars:
    '''It asks the user for a Github username and whether they want to preserve timestamps, and returns a
    `ResponseGithubStars` object with the username and preserve timestamps flag
    
    Returns
    -------
        A ResponseGithubStars object.
    
    '''
    username = input("Github username: ")
    preserve_timestamps_input = input("Preserve timestamps [Y/n]: ")
    preserve_timestamps = preserve_timestamps_input.lower() == "y"
    return ResponseGithubStars(username=username, preserve_timestamps=preserve_timestamps)

def clear_screen():
    clear = 'cls' if os.name == 'nt' else 'clear'
    os.system(clear)


def loop():
    options: dict[str, Option] = {
        "A": Option(name="Add a bookmark", command=commands.AddBookmarkCommand(),  prep_call=cast(Callable[..., Any], get_new_bookmark_data), success_message="Bookmark added!"),
        "B": Option(name="List bookmarks by date", command=commands.ListBookmarksCommand(order_by="title")),
        "T": Option(name="List bookmarks by title", command=commands.ListBookmarksCommand(order_by="date_added")),
        "D": Option(name="Delete a bookmark", command=commands.DeleteBookmarkCommand(),  prep_call=cast(Callable[..., str], get_delete_bookmark_data), success_message="Bookmark deleted!"),
        "E": Option(name="Edit a bookmark", command=commands.EditBookmarkCommand(),  prep_call=cast(Callable[..., Any], get_update_bookmark_data), success_message="Bookmark updated!"),
        "G": Option(name="Import Github stars", command=commands.ImportGithubStarsCommand(),  prep_call=cast(Callable[..., Any], get_github_stars_data), success_message="Github starts imported!"),
        "Q": Option(name="Quit", command=commands.QuitCommand())
    }
    print_options(options)
    print("")
    choice = cast(Option, get_user_choice(options))
    print("")
    choice.choose()
    print("")
    _ = input('Press ENTER to return to menu')
    clear_screen()

    
if __name__ == "__main__":
    commands.CreateBookmarksTableCommand().execute()
    while True:
        loop()