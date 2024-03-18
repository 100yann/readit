from fastapi import APIRouter, status
from .. import schemas

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


# Create a user
@router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate):
    ...

# Get user by id