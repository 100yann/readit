from fastapi import FastAPI, HTTPException, Form
from database import *

app = FastAPI()


@app.get("/get_all_posts")
def root():
    all_reviews = get_reviews()
    return {'reviews': all_reviews}


@app.post('/authenticate_user/')
def authenticate_user(email: str = Form(...), password: str = Form(...)):
    # check if email exists in db
    if not check_if_exists(
        columns='email', 
        table= 'users', 
        column= 'email', 
        value= email
        ):
        # email is invalid
        raise HTTPException(status_code=401, detail='Incorrect email')

    # check if password is valid
    if verify_password(password, email):
        user_id = get_user_id(email)
  
        return {'detail':'Login successful', 'data': {'user_id': user_id}}
    # password is invalid
    else:
        raise HTTPException(status_code=401, detail='Incorrect password')


@app.post('/save_user/')
def save_user_route(email: str = Form(...), password: str = Form(...)):
    # check if user exists
    if check_if_exists(
        columns='email', 
        table='users', 
        column='email', 
        value=email
    ):
        raise HTTPException(status_code=400, detail='User already exists')

    hashed_password = hash_password(password)

    # Save user
    save_user(email, hashed_password)

    return {"status": "success", "message": "User saved successfully"}


