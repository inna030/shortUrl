from pydantic import BaseModel, HttpUrl, validator
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, constr
class User(BaseModel):
    username: str
    password: str
    url_limit: int = 20
    created_urls: int = 0
    is_admin: bool = False

class URL(BaseModel):
    original_url: HttpUrl
    custom_short_url: Optional[str] = None
    expire_date: Optional[datetime] = None

    @validator('expire_date', pre=True, always=True)
    def validate_expire_date(cls, v):
        if v is not None:
            try:
                if isinstance(v, str):
                    return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError('Invalid datetime format. Expected format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS')
        return v

class URLUpdate(BaseModel):
    new_long_url: HttpUrl
    old_long_url: HttpUrl
    short_url: str

class CreateUserRequest(BaseModel):
    username: str
    password: str

class UpdateURLLimitRequest(BaseModel):
    username: str
    new_limit: int




class ChangePasswordRequest(BaseModel):
    old_password: constr(min_length=6)
    new_password: constr(min_length=6)
