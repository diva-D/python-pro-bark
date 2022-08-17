from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel

class Bookmark(BaseModel):
    title: str
    url: str
    notes: Optional[str] = None
    date_added: str = datetime.now(timezone.utc).isoformat()


class ResponseGithubStars(BaseModel):
    username: str
    preserve_timestamps: bool = True
    
class ResponseUpdateBookmark(BaseModel):
    column: str
    new_value: str
    id: str

class ResponseCommand(BaseModel):
    status: bool
    result: Optional[list[Any]]
    error: Optional[str] = None