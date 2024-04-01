from typing import Optional
from pydantic import BaseModel, EmailStr, ValidationError, Field
from datetime import datetime


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

    class Config:
        from_attributes = True


class ReviewData(BaseModel):
    id: int
    content: str
    date_read: str
    created_at: datetime
    owner:  UserDataOut

    class Config:
        from_attributes = True


class ReviewWithLikes(BaseModel):
    Reviews: ReviewData
    total_likes: int

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


class ValidBookRating(BaseModel):
    rating: int = Field(..., ge=1, le=5)
