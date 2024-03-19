from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    content: str
    date_read: str
    reviewed_by: int

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