from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class URL(BaseModel):
    short_url: Optional[str] = None
    original_url: str
    expire_date: Optional[datetime] = None

class URLUpdate(BaseModel):
    new_long_url: HttpUrl
    old_long_url: HttpUrl
    short_url: str
