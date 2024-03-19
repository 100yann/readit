from fastapi import APIRouter, Depends
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
@router.post('/')
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


# Update a review


# Get post by ID 