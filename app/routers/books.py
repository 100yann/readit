from fastapi import APIRouter, Depends, status, Response, HTTPException, Body
from .. import schemas, models, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional


router = APIRouter(
    prefix='/book',
    tags=['Books']
)


# Save book to bookshelf
@router.post('/shelve/{book_id}')
def shelve_book(book_id: str,
                data: schemas.BookshelfData,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):

    is_saved = db.query(
        models.Bookshelves).filter(
        models.Bookshelves.book_id == book_id,
        models.Bookshelves.user_shelved == data.user_id,
        models.Bookshelves.bookshelf == data.bookshelf)

    # if book is already shelved unshelve it
    if is_saved.first():
        is_saved.delete(synchronize_session=False)
        db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # else save it to db
    utils.save_book_to_bookshelf(
        user_id=data.user_id,
        book_id=book_id,
        bookshelf=data.bookshelf,
        db=db
    )

    return Response(status_code=status.HTTP_201_CREATED)


@router.get('/find/{title}')
def find_book_by_title(title: str, db: Session = Depends(get_db)):
    # gets all matches from the db
    matches = db.query(
        models.Books).filter(
        models.Books.title.ilike(f'%{title}%')).all()

    # gets 5 matches from google apis
    google_matches = utils.get_books_by_title(title)

    if not matches and not google_matches:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Could not find any matching books')

    if google_matches:
        # check if book is already saved to db by comparing isbn to avoid
        # duplicate results
        db_isbns = {book.isbn for book in matches}
        for book in google_matches:
            if book['isbn'] not in db_isbns:
                matches.append(book)

    return matches


@router.post('/rate/{book_id}')
def rate_book(book_id: int,
              book_rating: schemas.ValidBookRating,
              db: Session = Depends(get_db),
              current_user: int = Depends(oauth2.get_current_user)
              ):
    query = db.query(models.BookRatings).\
        filter(models.BookRatings.book_id == book_id,
               models.BookRatings.user_id == current_user.id).\
        first()

    if query:
        query.rating = book_rating.rating
    else:
        new_rating = models.BookRatings(book_id=book_id,
                                        user_id=current_user.id,
                                        rating=book_rating.rating
                                        )
        db.add(new_rating)

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Book not found')

    return Response(status_code=status.HTTP_201_CREATED)


@router.get('/get/{book_isbn}', response_model=schemas.DisplayBookData)
def get_book_data(book_isbn: str,
                  user_id: str | None = None,
                  db: Session = Depends(get_db)
                  ):
    book = db.query(models.Books).filter(models.Books.isbn == book_isbn).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Book nott found')
    
    reviews_query = db.query(models.Reviews).filter(models.Reviews.book_reviewed == book.id).all()

    if user_id:
        bookshelf = db.query(
                models.Bookshelves
            ).filter(
                models.Bookshelves.book_id == book.id, 
                models.Bookshelves.user_shelved == user_id
            ).first()
        
        rating = db.query(
                models.BookRatings
            ).filter(
                models.BookRatings.book_id == book.id,
                models.BookRatings.user_id == user_id
            ).first()
    
        return {
            'reviews': reviews_query,
            'shelf': bookshelf.bookshelf,
            'rating': rating 
        }
    
    return {'reviews': reviews_query}