from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        from_attributes = True


class UserDataOut(BaseModel):
    email: EmailStr
    id: int

    class Config:
        from_attributes = True

        
class ReviewCreate(BaseModel):
    content: str
    date_read: str

    class Config:
        from_attributes = True


class ReviewUpdate(BaseModel):
    content: str
    user_id: int

    class Config:
        from_attributes = True


class BookData(BaseModel):
    isbn: str
    title: str
    author: str
    thumbnail: str

    class Config:
        from_attributes = True


class BookshelfData(BaseModel):
    user_id: str
    bookshelf: str


class JwtToken(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None