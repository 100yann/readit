from fastapi import APIRouter, Depends, status, Response, HTTPException, Body
from .. import schemas, models, utils
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func


router = APIRouter(
    prefix='/book',
    tags=['Books']
)


# Save book to bookshelf
@router.post('/shelve/{book_id}')
def shelve_book(book_id: str, 
                data: schemas.BookshelfData, 
                db: Session = Depends(get_db)):
    
    is_saved = db.query(models.Bookshelves).filter(models.Bookshelves.book_id == book_id, 
                                                   models.Bookshelves.user_shelved == data.user_id,
                                                   models.Bookshelves.bookshelf == data.bookshelf
                                                   )
    
    # if book is already shelved unshelve it
    if is_saved.first(): 
        is_saved.delete(synchronize_session=False)
        db.commit()
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # else save it to db
    utils.save_book_to_bookshelf(
        user_id = data.user_id, 
        book_id = book_id, 
        bookshelf= data.bookshelf, 
        db=db
    )
    
    return {'details': 'success'}


@router.get('/find/{title}')
def find_book_by_title(title: str, db: Session = Depends(get_db)):
    matches = db.query(models.Books).filter(models.Books.title.ilike(f'%{title}%')).all()

    if not matches:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = 'Could not find any matching books')
    
    return matches