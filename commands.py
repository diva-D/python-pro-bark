from datetime import datetime
from typing import Optional
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
        
        
    
