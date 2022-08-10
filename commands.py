from datetime import datetime
import sys
from typing import Optional, Union
from database import DatabaseManager
from datetime import timezone
from pydantic import BaseModel, ValidationError

db = DatabaseManager("bookmarks.db")




class Bookmark(BaseModel):
    title: str
    url: str
    notes: Optional[str] = None
    date_added: str = datetime.now(timezone.utc).isoformat()

class CreateBookmarksTableCommand:
    def execute(self):
        bookmark_columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "title": "TEXT NOT NULL",
            "url": "TEXT NOT NULL",
            "notes": "TEXT",
            "date_added": "TEXT NOT NULL",
        }
        db.create_table("bookmarks", bookmark_columns)


class AddBookmarkCommand:
    def execute(self, bookmark_data: dict[str, str]) -> str:
        try:
            bookmark = Bookmark(**bookmark_data)
            db.add("bookmarks", bookmark.dict())
            
            return f"Bookmark for {bookmark.title} added!"
            
        except ValidationError as e:
            return repr(e)
        

class ListBookmarksCommand:
    def __init__(self, order_by: Union[None, str] = "date_added"):
        self.order_by = order_by
    
    def execute(self) -> list[str]:
        cursor = db.select(table="bookmarks", order_by=self.order_by)
        return cursor.fetchall()


class DeleteBookmarkCommand:
    def execute(self, id: str) -> str:
        db.delete("bookmarks", criteria={"id": id})
        return "Bookmark deleted!"
    
class QuitCommand:
    def execute(self) -> None:
        sys.exit()