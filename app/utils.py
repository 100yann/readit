from .database import get_db
from . import models
from sqlalchemy.orm import Session


def save_book_to_bookshelf(user_id, book_id, bookshelf, db: Session):
    bookshelf_entry = models.Bookshelves(book_id=book_id, 
                                         user_shelved=int(user_id), 
                                         bookshelf=bookshelf
                                         )
    db.add(bookshelf_entry)
    db.commit()
    db.refresh(bookshelf_entry)
    return bookshelf_entry