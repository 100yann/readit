from fastapi import FastAPI, HTTPException, Form, Request
from database import *
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


@app.get("/get_reviews")
def get_all_reviews():
    all_reviews = get_reviews()
    return {'reviews': all_reviews}


@app.post('/authenticate_user')
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


@app.post('/save_user')
def save_user_route(email: str = Form(...), 
                    password: str = Form(...),
                    first_name: str = Form(...),
                    last_name: str = Form(...),
                    ):
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
    save_user(email, hashed_password, first_name, last_name)

    return {"status": "success", "message": "User saved successfully"}


class ReviewData(BaseModel):
    bookIsbn: str
    bookTitle: str
    bookAuthor: str
    bookDescription: str
    bookThumbnail: str
    review: str
    date_read: str
    reviewed_by: int


@app.post("/save_review")
def save_review(request: Request, data: ReviewData):  
    reviewed_by = data.reviewed_by

    book_isbn = data.bookIsbn
    # Check if book isn't saved to DB
    if not check_if_exists('id', 'book_details', 'isbn', book_isbn):
        # Save book to DB
        columns = ['title', 'author', 'description', 'isbn', 'thumbnail']
        values = [
            data.bookTitle, 
            data.bookAuthor, 
            data.bookDescription,
            book_isbn,
            data.bookThumbnail,
            ]
        insert_into_db(columns, values, 'book_details')

    # Get the id of the book reviewed
    book_id = get_book_id_by_isbn(book_isbn)[0]

    # save review
    columns = ['review_content', 'date_read', 'book_reviewed', 'reviewed_by']
    values = [data.review, data.date_read, book_id, reviewed_by]
    insert_into_db(columns, values, 'reviews')

    return {'status': 'success', 'message': 'Review saved successfully'}