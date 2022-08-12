from datetime import datetime
from os import environ
import sys
from typing import Optional, Union, Any
from database import DatabaseManager
from datetime import timezone
from pprint import pprint
from pydantic import BaseModel, ValidationError, parse_obj_as

import requests
from pydantic_types import StarredRepo, ResponseGithubStars

db = DatabaseManager("bookmarks.db")




class Bookmark(BaseModel):
    title: str
    url: str
    notes: Optional[str] = None
    date_added: str = datetime.now(timezone.utc).isoformat()
    
class Command:
    pass

class CreateBookmarksTableCommand(Command):
    def execute(self) -> None:
        bookmark_columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "title": "TEXT NOT NULL",
            "url": "TEXT NOT NULL",
            "notes": "TEXT",
            "date_added": "TEXT NOT NULL",
        }
        db.create_table("bookmarks", bookmark_columns)


class AddBookmarkCommand(Command):
    def execute(self, bookmark_data: dict[str, Optional[str]]) -> str:
        try:
            bookmark = Bookmark.parse_obj(bookmark_data)
            db.add("bookmarks", bookmark.dict())
            
            return f"Bookmark for {bookmark.title} added!"
            
        except ValidationError as e:
            return (str(e))
        

class ListBookmarksCommand(Command):
    def __init__(self, order_by: Union[None, str] = "date_added"):
        self.order_by = order_by
    
    def execute(self) -> list[Any]:
        cursor = db.select(table="bookmarks", order_by=self.order_by)
        return pprint(cursor.fetchall())


class DeleteBookmarkCommand(Command):
    def execute(self, id: str) -> str:
        db.delete("bookmarks", criteria={"id": id})
        return "Bookmark deleted!"
    
class QuitCommand(Command):
    def execute(self) -> None:
        sys.exit()
        
class ImportGithubStarsCommand(Command):
    base_url: str = "https://api.github.com/"
        
    def _get_starred_repos(self, username: str) -> list[StarredRepo]:
        endpoint = "user/starred"
        headers = {
            "Accept": "application/vnd.github.v3.star+json",
            "Authorization": f"token {environ.get('GITHUB_TOKEN')}"
        }
        response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
        starred_repos: Union[list[StarredRepo], list[Any]] = parse_obj_as(list[StarredRepo], response.json())
        while 'next' in response.links.keys():
            response = requests.get(response.links['next']['url'],headers=headers)
            starred_repos.extend(parse_obj_as(list[StarredRepo], response.json()))
        return starred_repos
    
    def _create_bookmark_data(self, starred_repo: StarredRepo, preserve_timestamps: bool = True) -> dict[str, Union[str, None]]:
        repo = starred_repo.repo
        bookmark_data = {
            "title": repo.name,
            "url": repo.html_url,
            "notes": repo.description
        }
        if preserve_timestamps:
            bookmark_data["date_added"] = starred_repo.starred_at
            
        return bookmark_data
    
    def execute(self, data: ResponseGithubStars) -> None:
        # get starred repos
        starred_repos: list[StarredRepo] = self._get_starred_repos(data.username)
        for starred_repo in starred_repos:
            bookmark_data = self._create_bookmark_data(starred_repo, data.preserve_timestamps)
            AddBookmarkCommand().execute(bookmark_data=bookmark_data)
        print(f"Imported {len(starred_repos)} from starred repos")