from fastapi import APIRouter, Depends, status, Response, HTTPException, Body
from .. import schemas, models, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from typing import List

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


# Create a user
@router.post('/create',
             status_code=status.HTTP_201_CREATED,
             response_model=schemas.UserDataOut)
def create_user(user: schemas.UserCreate,
                db: Session = Depends(get_db)
                ):

    new_user = db.query(models.Users).filter(
        models.Users.email == user.email).first()
    if new_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='User with this email already exists')

    hashed_pw = utils.hash_password(user.password)

    new_user = models.Users(email=user.email,
                            password=hashed_pw,
                            )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user_details = models.UserDetails(id=new_user.id,
                                      first_name=user.first_name,
                                      last_name=user.last_name
                                      )

    db.add(user_details)
    db.commit()
    return new_user


# Get user by id
@router.get('/{id}', response_model=schemas.UserProfileData)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with ID {id} not found')

    user_details = db.query(models.UserDetails).filter(models.UserDetails.id == user.id).first()

    books = db.query(
        models.Bookshelves,
        models.Books
        ).join(models.Books, models.Books.id == models.Bookshelves.book_id
        ).filter(models.Bookshelves.user_shelved == user.id
        ).all()
    
    return {'user': user, 'user_details': user_details, 'books': books}


@router.post('/login')
def login(user_crendetials: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):

    user = utils.authenticate_user(db, user_crendetials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = oauth2.create_access_token(data={'user_id': user.id})
    name_query = db.query(
        models.UserDetails.first_name, models.UserDetails.last_name
        ).\
        filter(models.UserDetails.id == user.id).\
        first()
    
    name = f'{name_query[0]} {name_query[1]}'
    print(name)
    return {'access_token': access_token, 'token_type': 'bearer', 'name': name, 'id': user.id}
