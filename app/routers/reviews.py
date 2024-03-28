from fastapi import APIRouter, Depends, status, Response, HTTPException
from .. import schemas, models, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional


router = APIRouter(
    prefix='/reviews',
    tags=['Reviews']
)


# Get all reviews
@router.get('/', response_model=List[schemas.ReviewOut])
def get_reviews(user_id: int | None = None, 
                db: Session = Depends(get_db)):
    
    if user_id:
        reviews = db.query(models.Reviews).filter(models.Reviews.reviewed_by == user_id).all()
    else:
        reviews = db.query(models.Reviews).all()

    return reviews


# Get most recent reviews
@router.get('/recent', response_model=List[schemas.ReviewOut])
def get_recent_reviews(num_reviews: int = 5, db: Session = Depends(get_db)):
    reviews = db.query(models.Reviews).\
        order_by(models.Reviews.created_at.desc()).\
        limit(num_reviews).\
        all()
    return reviews


# Get review by ID
@router.get('/{id}', response_model=schemas.ReviewOut)
def get_review_by_id(id: str, db: Session = Depends(get_db)):
    review = db.query(models.Reviews).filter(models.Reviews.id == id).first()

    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Review with ID {id} not found')

    return review


# Create a review
@router.post('/', status_code=status.HTTP_201_CREATED)
def create_review(review: schemas.ReviewCreate,
                  book: schemas.BookData,
                  current_user: int = Depends(oauth2.get_current_user),
                  db: Session = Depends(get_db),
                  ):
    
    # Check if the book reviewed already exists in the db
    book_exists = db.query(
        models.Books).filter(
        models.Books.isbn == book.isbn).first()
    
    if not book_exists:
        # if not - save it
        book_exists = models.Books(**book.model_dump())
        db.add(book_exists)
        db.commit()
        db.refresh(book_exists)

    # Save review
    new_review = models.Reviews(**review.model_dump())
    new_review.book_reviewed = book_exists.id
    new_review.owner_id = current_user.id

    # Save book to bookshelf
    utils.save_book_to_bookshelf(
        user_id=current_user.id,
        book_id=book_exists.id,
        bookshelf='bookshelf',
        db=db
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


# Delete a review
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_review(id: int, 
                  db: Session = Depends(get_db),
                  current_user: int = Depends(oauth2.get_current_user)
                  ):
    
    review_query = db.query(models.Reviews).filter(models.Reviews.id == id)
    review = review_query.first()
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Review with ID{id} does not exist')

    if review.reviewed_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Unauthorized to delete this post')
    
    review_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Update a review
@router.patch('/{id}')
def update_review(id: str,
                  new_review: schemas.ReviewUpdate,
                  db: Session = Depends(get_db),
                  current_user: int = Depends(oauth2.get_current_user)
                  ):
    
    review = db.query(models.Reviews).filter(models.Reviews.id == id).first()

    # check if review doesn't exist
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Review with ID{id} does not exist')

    # check if the creator of the review made the request
    if review.reviewed_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized to update this post')

    # update the review
    review.content = new_review.content
    db.commit()
    db.refresh(review)

    return review


# Like a review
@router.post('/like/{review}')
def like_review(review: int,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)
                ):

    has_liked = db.query(models.Likes).\
        filter(models.Likes.review_id == review).\
        filter(models.Likes.user_id == current_user.id)

    # check if this review has already been liked by this user
    if has_liked.first():
        # if yes - unlike it
        has_liked.delete(synchronize_session=False)
        db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # like the review
    like = models.Likes(review_id=review, user_id=current_user.id)
    db.add(like)

    try:
        db.commit()
    except IntegrityError as e:
        # if a review or user with the specified id does not exist raise an
        # exception
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User or review not found')
    else:
        db.refresh(like)

    return like
