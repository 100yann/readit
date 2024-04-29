from typing import Optional, List, Tuple, Dict
from pydantic import BaseModel, EmailStr, ValidationError, Field
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    
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
    id: int
    isbn: str
    title: str
    author: str
    thumbnail: str

    class Config:
        from_attributes = True


class ReviewWithBookData(BaseModel):
    id: int
    Users: UserDataOut
    first_name: str
    last_name: str
    Books: BookData

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


class RateBook(BaseModel):
    rating: int = Field(..., ge=1, le=5)


class UserDetails(BaseModel):
    first_name: str
    last_name: str
    birthday: Optional[datetime] | None = None
    country: Optional[str] | None = None


class BookshelfData(BaseModel):
    id: int
    book_id: int
    bookshelf: str
    user_shelved: int


class BooksAndShelvesData(BaseModel):
    Bookshelves: BookshelfData
    Books: BookData


class UserProfileData(BaseModel):
    user: UserDataOut
    user_details: UserDetails
    books: List[BooksAndShelvesData]


class DisplayBookData(BaseModel):
    reviews: List[ReviewData]
    shelf: Tuple | None = None
    rating: Optional[int] | None = None
    book_id: int
    book_stats: Dict


class Bookshelf(BaseModel):
    shelf: str