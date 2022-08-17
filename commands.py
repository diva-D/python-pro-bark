import sys
from typing import Optional, Union, Any
from pydantic import BaseModel, ValidationError, parse_obj_as
from abc import ABC, abstractmethod

import requests
from persistence import BookmarkDatabase
from pydantic_types import Bookmark, StarredRepo, ResponseUpdateBookmark, ResponseGithubStars, ResponseCommand

persistence = BookmarkDatabase()
class Command(BaseModel, ABC):
    @abstractmethod
    def execute(self, data: Any) -> Optional[ResponseCommand]:
        raise NotImplementedError

class CreateBookmarksTableCommand(Command):
    def execute(self, data: None = None) -> ResponseCommand:
        
        return ResponseCommand(status=True, result=None)


class AddBookmarkCommand(Command):
    def execute(self, data: dict[str, Optional[str]]) -> ResponseCommand:
        try:
            bookmark = Bookmark.parse_obj(data)
            persistence.create(bookmark.dict())
            
            return ResponseCommand(status=True, result=None)
            
        except ValidationError as e:
            print(e)
            return ResponseCommand(status=False, result=None, error=str(e))
        

class ListBookmarksCommand(Command):
    order_by: Optional[str] = "date_added"
    
    def execute(self, data: None = None) -> ResponseCommand:
        cursor = persistence.list(order_by=self.order_by)
        return ResponseCommand(status=True, result=cursor.fetchall())


class DeleteBookmarkCommand(Command):
    def execute(self, data: str) -> ResponseCommand:
        persistence.delete(bookmark_id=data)
        return ResponseCommand(status=True, result=None)
    
class EditBookmarkCommand(Command):
    def execute(self, data: ResponseUpdateBookmark) -> ResponseCommand:
        persistence.edit(bookmark_id=data.id, data={data.column: data.new_value})
        return ResponseCommand(status=True, result=None)
    
class QuitCommand(Command):
    def execute(self, data: None = None) -> None:
        sys.exit()
        
class ImportGithubStarsCommand(Command):
    base_url: str = "https://api.github.com/"
        
    def _get_starred_repos(self, username: str) -> list[StarredRepo]:
        """
        It gets the starred repos of a user.
        
        :param username: str - The username of the user whose starred repos you want to get
        :type username: str
        :return: A list of StarredRepo objects
        """
        endpoint = f"users/{username}/starred"
        headers = {
            "Accept": "application/vnd.github.v3.star+json",
            # "Authorization": f"token {environ.get('GITHUB_TOKEN')}"
        }
        response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
        starred_repos: Union[list[StarredRepo], list[Any]] = parse_obj_as(list[StarredRepo], response.json())
        while 'next' in response.links.keys():
            response = requests.get(response.links['next']['url'],headers=headers)
            starred_repos.extend(parse_obj_as(list[StarredRepo], response.json()))
        return starred_repos
    
    def _create_bookmark_data(self, starred_repo: StarredRepo, preserve_timestamps: bool = True) -> dict[str, Union[str, None]]:
        """
        > This function takes a `StarredRepo` object and returns a dictionary with the keys `title`,
        `url`, `notes`, and `date_added`
        
        :param starred_repo: StarredRepo
        :type starred_repo: StarredRepo
        :param preserve_timestamps: If True, the date_added field of the bookmark will be set to the
        date the repo was starred. If False, the date_added field will be set to the current date,
        defaults to True
        :type preserve_timestamps: bool (optional)
        :return: A dictionary with the title, url, notes, and date_added.
        """
        repo = starred_repo.repo
        bookmark_data = {
            "title": repo.name,
            "url": repo.html_url,
            "notes": repo.description
        }
        if preserve_timestamps:
            bookmark_data["date_added"] = starred_repo.starred_at
            
        return bookmark_data
    
    def execute(self, data: ResponseGithubStars) -> ResponseCommand:
        # get starred repos
        starred_repos: list[StarredRepo] = self._get_starred_repos(data.username)
        for starred_repo in starred_repos:
            bookmark_data = self._create_bookmark_data(starred_repo, data.preserve_timestamps)
            AddBookmarkCommand().execute(data=bookmark_data)
        return ResponseCommand(status=True, result=None)