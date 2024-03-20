from fastapi import APIRouter, Depends, status, Response, HTTPException, Body
from .. import schemas, models, utils
from ..database import get_db
from sqlalchemy.orm import Session


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
                                                   models.Bookshelves.user_shelved == data.user_id
                                                   )
    
    if is_saved.first(): 
        is_saved.delete(synchronize_session=False)
        db.commit()
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    utils.save_book_to_bookshelf(
        user_id = data.user_id, 
        book_id = book_id, 
        bookshelf= data.bookshelf, 
        db=db
    )
    
    return {'details': 'success'}