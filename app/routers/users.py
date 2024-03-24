from fastapi import APIRouter, Depends, status, Response, HTTPException, Body
from .. import schemas, models, utils
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

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
    
    hashed_pw = utils.hash_password(user.password)
    user_dict = user.model_dump()
    user_dict['password'] = hashed_pw

    new_user = models.Users(**user_dict)

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


@router.post('/login')
def login(user_crendetials: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    
    user = db.query(models.Users).filter(models.Users.email == user_crendetials.username).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = 'Invalid email')
    
    if not utils.verify_password(plain_password = user_crendetials.password, 
                                 hashed_password = user.password
                                 ):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail = 'Invalid password')
    
    return {'message': 'successful login'}