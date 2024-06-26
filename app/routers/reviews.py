from fastapi import APIRouter, Depends, status, Response, HTTPException
from .. import schemas, models, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from sqlalchemy.sql.functions import func
from sqlalchemy import select, exists


router = APIRouter(
    prefix='/reviews',
    tags=['Reviews']
)


# Get all reviews
@router.get('/', response_model=List[schemas.ReviewWithLikes])
def get_reviews(user_id: int | None = None,
                book_isbn: str | None = None,
                db: Session = Depends(get_db)):

    review_query = db.query(
        models.Reviews,
        func.count(
            models.Likes.review_id).label('total_likes')). join(
        models.Likes,
        models.Reviews.id == models.Likes.review_id,
        isouter=True). group_by(
                models.Reviews.id)
    
    # get reviews created by this user
    if user_id:
        reviews = review_query.filter(models.Reviews.owner_id == user_id).all()

    # get reviews for book with provided isbn
    elif book_isbn:
        book_id = db.query(models.Books).filter(models.Books.isbn == book_isbn).first()
        if not book_id:
            # if book not found raise HTTP exception
            raise HTTPException(status=status.HTTP_404_NOT_FOUND,
                                detail='Book not found')
        
        reviews = review_query.filter(models.Reviews.book_reviewed == book_id.id).all()
    
    # else return all reviews
    else:
        reviews = review_query.all()

    if not reviews:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='No reviews found')
    return reviews


# Get most recent reviews
@router.get('/recent', response_model=List[schemas.ReviewWithBookData])
def get_recent_reviews(num_reviews: int = 5, db: Session = Depends(get_db)):
    reviews = db.query(
        models.Reviews.id,
        models.Users,
        models.UserDetails.first_name,
        models.UserDetails.last_name,
        models.Books
    ).join(
        models.Books, models.Reviews.book_reviewed == models.Books.id
    ).join(
        models.Users, models.Reviews.owner_id == models.Users.id
    ).join(
        models.UserDetails, models.Users.id == models.UserDetails.id
    ).order_by(
        models.Reviews.created_at.desc()
    ).limit(
        num_reviews
    ).all()

    return reviews


# Get review by ID
@router.get('/{id}', response_model=schemas.ReviewWithLikes)
def get_review_by_id(id: str, db: Session = Depends(get_db)):
    review = db.query(
        models.Reviews,
        func.count(
            models.Likes.review_id).label('total_likes')). join(
        models.Likes,
        models.Reviews.id == models.Likes.review_id,
        isouter=True). group_by(
                models.Reviews.id). first()

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
@router.delete('/{review_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int,
                  db: Session = Depends(get_db),
                  current_user: int = Depends(oauth2.get_current_user)
                  ):

    review_query = db.query(models.Reviews).filter(models.Reviews.id == review_id)
    review = review_query.first()
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Review with ID{review_id} does not exist')

    if review.owner_id != current_user.id:
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
@router.post('/like/{review}', status_code=status.HTTP_201_CREATED)
def like_review(review: int,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)
                ):
    has_liked = db.query(models.Likes).\
        filter(models.Likes.review_id == review).\
        filter(models.Likes.user_id == current_user.id)

    # check if this review has already been liked by this user
    if has_liked.first():
        # unlike the review
        has_liked.delete(synchronize_session=False)
        db.commit()
        message = 'Unliked'

    # like the review
    else:
        like = models.Likes(review_id=review, user_id=current_user.id)
        db.add(like)
        try:
            db.commit()
        except IntegrityError:
            # if a review or user with the specified id does not exist
            # raise an exception
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='User or review not found')
        else:
            db.refresh(like)
            message = 'Liked'

    return {'status': message}

@router.get('/book/{book_id}', response_model=List[schemas.ReviewWithLikes])
def get_reviews_by_book(book_id: str,
                        page: int | None = None,
                        user_id: str | None = None, 
                        db: Session = Depends(get_db)
                        ):
    if not user_id:
        reviews_query = db.query(
            models.Reviews,
            func.count(models.Likes.id).label('total_likes')
            ).join(
                models.Likes, models.Likes.review_id == models.Reviews.id, isouter=True
            ).group_by(
                models.Reviews.id
            ).filter(
                models.Reviews.book_reviewed == book_id
            ).limit(5)
    else:
        # create a subquery that checks if the current user has liked a review
        exists_criteria = (
            select(models.Likes.review_id).
            where(models.Likes.user_id == user_id).
            where(models.Likes.review_id == models.Reviews.id).
            exists()
            ).correlate(models.Reviews)
        
        reviews_query = db.query(
            models.Reviews,
            func.count(models.Likes.id).label('total_likes'),
            exists_criteria.label('has_user_liked')
            ).join(
                models.Likes, models.Likes.review_id == models.Reviews.id, isouter=True
            ).group_by(
                models.Reviews.id
            ).filter(
                models.Reviews.book_reviewed == book_id
            ).limit(5)
        
    skip_num_reviews = (page - 1) * 5
    reviews = reviews_query.offset(skip_num_reviews).all()
    return reviews