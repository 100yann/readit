from fastapi import APIRouter, Depends, status, Response, HTTPException
from .. import schemas, models
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix='/reviews',
    tags=['Reviews']
)


# Get all reviews
@router.get('/')
def get_reviews(db: Session = Depends(get_db)):
    reviews = db.query(models.Reviews).all()
    return reviews


# Create a review
@router.post('/', status_code=status.HTTP_201_CREATED)
def create_review(review: schemas.ReviewCreate,
                  book: schemas.BookData,
                  db: Session = Depends(get_db)
                  ):
    
    # Check if the book reviewed already exists in the db
    book_exists = db.query(models.Books).filter(models.Books.isbn == book.isbn).first()
    if not book_exists:
        # if not - save it
        book_exists = models.Books(**book.model_dump())
        db.add(book_exists)
        db.commit()
        db.refresh(book_exists)

    # Save review
    new_review = models.Reviews(**review.model_dump())
    new_review.book_reviewed = book_exists.id
    
    db.add(new_review)  
    db.commit() 
    db.refresh(new_review)

    return new_review


# Delete a review
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_review(id: int, db: Session = Depends(get_db)):
    query = db.query(models.Reviews).filter(models.Reviews.id == id)

    if query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Review with ID{id} does not exist')
    
    query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
# Update a review


# Get post by ID 