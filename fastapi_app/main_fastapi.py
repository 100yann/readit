from fastapi import FastAPI, HTTPException
from database import *

app = FastAPI()

@app.get("/get_all_posts")
def root():
    all_reviews = get_reviews()
    return {'reviews': all_reviews}


@app.post('/authenticate_user/')
def authenticate_user(email:str, password:str):
    # check if email exists in db
    if not check_existing(
        columns='email', 
        table= 'users', 
        column= 'email', 
        value= email
        ):
        # email is invalid
        raise HTTPException(status_code=401, detail='Incorrect email')

    # check if password is valid
    if verify_password(password, email):
        raise HTTPException(status_code=200, detail='Login successful')
    # password is invalid
    else:
        raise HTTPException(status_code=401, detail='Incorrect password')


@app.post('/save_user/')
def save_user(email:str, password:str):
    hashed_password = hash_password(password)

    # Save user
    if not save_user(email, hashed_password):
        raise HTTPException(status_code=400, detail='User already exists')

    return {"status": "success", "message": "User saved successfully"}