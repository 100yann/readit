from fastapi import APIRouter, Depends, status, Response, HTTPException, Body
from .. import schemas, models, utils
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix='/users',
    tags=['Users']
)


# Create a user
@router.post('/', 
             status_code=status.HTTP_201_CREATED, 
             response_model=schemas.UserDataOut)
def create_user(user: schemas.UserCreate, 
                db: Session = Depends(get_db)
                ):
    new_user = db.query(models.Users).filter(models.Users.email == user.email).first()
    if new_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            details = 'User with this email already exists')
    
    new_user = models.Users(**user.model_dump())

    db.add(new_user)  
    db.commit() 
    db.refresh(new_user)

    return new_user


# Get user by id
@router.get('/{id}', response_model=schemas.UserDataOut)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with ID {id} not found')
    
    return user