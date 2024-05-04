from fastapi import APIRouter, Depends, status, Response, HTTPException, Body
from .. import schemas, models, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import func


router = APIRouter(
    prefix='/book',
    tags=['Books']
)


# Save book to bookshelf
@router.post('/shelve/{book_isbn}')
def shelve_book(book_isbn: str,
                bookshelf: schemas.Bookshelf,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)
                ):
    book = db.query(models.Books).filter(models.Books.isbn == book_isbn).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Book not found')
    
    is_saved = db.query(
        models.Bookshelves).filter(
        models.Bookshelves.book_id == book.id,
        models.Bookshelves.user_shelved == current_user.id,
        models.Bookshelves.bookshelf == bookshelf.shelf)

    # if book is already shelved unshelve it
    if is_saved.first():
        is_saved.delete(synchronize_session=False)
        db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # else save it to db
    utils.save_book_to_bookshelf(
        user_id=current_user.id,
        book_id=book.id,
        bookshelf=bookshelf.shelf,
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


@router.get('/get/{book_isbn}', response_model=schemas.DisplayBookData)
def get_book_data(book_isbn: str,
                  page: str | None = None,
                  user_id: str | None = None,
                  db: Session = Depends(get_db)
                  ):
    book = db.query(models.Books).filter(models.Books.isbn == book_isbn).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Book not found')
    
    avg_book_rating = db.query(
        func.avg(models.BookRatings.rating
                ).label('average_rating'),
        func.count(models.BookRatings.rating
                ).label('num_ratings')
        ).filter(models.BookRatings.book_id == book.id
        ).first()
    
    num_of_reviews = db.query(
        func.count(models.Reviews.id
                   ).label('num_reviews')
        ).filter(models.Reviews.book_reviewed == book.id
        ).all()
    
    book_stats = {
        'avg_book_rating': round(float(avg_book_rating.average_rating), 1),
        'num_ratings': avg_book_rating.num_ratings,
        'num_reviews': num_of_reviews[0].num_reviews
    }

    output = {
        'book_id': book.id,
        'book_stats': book_stats
        }
    
    if user_id:
        bookshelf = db.query(
                models.Bookshelves.bookshelf
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

        output['shelf'] = bookshelf
        output['rating'] = rating.rating
    
    return output



@router.post('/rate/{id}')
def rate_book(id: int,
              body: schemas.RateBook,
              db: Session = Depends(get_db),
              current_user: int = Depends(oauth2.get_current_user)
              ):
    query = db.query(models.BookRatings).\
        filter(models.BookRatings.book_id == id,
               models.BookRatings.user_id == current_user.id).\
        first()

    if query:
        query.rating = body.rating
    else:
        new_rating = models.BookRatings(book_id=id,
                                        user_id=current_user.id,
                                        rating=body.rating
                                        )
        db.add(new_rating)

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Book not found')

    return Response(status_code=status.HTTP_201_CREATED)
