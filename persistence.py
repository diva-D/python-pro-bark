from abc import ABC, abstractmethod
from sqlite3 import Cursor
from typing import Any, Optional

from database import DatabaseManager

class PersistenceLayer(ABC):    
    @abstractmethod
    def create(self, data: Any) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def list(self, order_by: Optional[str]) -> Any:
        raise NotImplementedError
        
    @abstractmethod
    def edit(self, bookmark_id: str, data: Any) -> None:
        raise NotImplementedError
        
    @abstractmethod
    def delete(self, bookmark_id: str) -> None:
        raise NotImplementedError
        

class BookmarkDatabase(PersistenceLayer):
    def __init__(self):
        self.table_name = "bookmarks"
        self.db = DatabaseManager(self.table_name)
        self.db.create_table("bookmarks", columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "title": "TEXT NOT NULL",
            "url": "TEXT NOT NULL",
            "notes": "TEXT",
            "date_added": "TEXT NOT NULL",
        })
        
    def create(self, data: dict[str, str]) -> None:
        self.db.add(table=self.table_name, data=data)
        
    def list(self, order_by: Optional[str] = "date_added") -> Cursor:
        return self.db.select(table=self.table_name, order_by=order_by)
    
    def edit(self, bookmark_id: str, data: Any) -> None:
        self.db.update(table=self.table_name, columns=data, criteria={"id": bookmark_id})
        
    def delete(self, bookmark_id: str) -> None:
        self.db.delete(table=self.table_name, criteria={"id": bookmark_id})