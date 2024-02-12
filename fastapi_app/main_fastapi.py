from fastapi import FastAPI, HTTPException, Form, Request, Body
from database import *
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


@app.get("/get_reviews")
def get_all_reviews(isbn: str | None = None, 
                    user_id: str | None = None,
                    page: str | None = None):
    
    if page == 'home':
        reviews = get_reviews(order='created_on desc', limit=5)
    else:
        reviews = get_reviews(isbn)
        if user_id:
            for index, review in enumerate(reviews):
                has_user_liked = check_if_exists(
                    columns = 'like_id',
                    table = 'review_likes',
                    condition1= 'review_id',
                    value1= review['review_id'],
                    condition2= 'user_id',
                    value2= user_id
                    ) 
                if has_user_liked:
                    reviews[index]['has_liked'] = True
    return {'reviews': reviews}


@app.post('/authenticate_user')
def authenticate_user(email: str = Form(...), password: str = Form(...)):
    # check if email exists in db
    if not check_if_exists(
        columns='email', 
        table= 'users', 
        condition1= 'email', 
        value1= email
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
        condition1='email', 
        value1=email
    ):
        raise HTTPException(status_code=400, detail='User already exists')

    hashed_password = hash_password(password)

    # Save user
    save_user(email, hashed_password, first_name, last_name)
    user_id = get_user_id(email)

    return {'detail':'Register successful', 'data': {'user_id': user_id}}


class ReviewData(BaseModel):
    bookIsbn: str
    bookTitle: str
    bookAuthor: str
    bookThumbnail: str
    review: str
    date_read: str
    reviewed_by: int

@app.post("/save_review")
def save_review(data: ReviewData):  
    book_isbn = data.bookIsbn
    # Check if book isn't saved to DB
    if not check_if_exists('book_id', 'books', 'isbn', book_isbn):
        # Save book to DB
        columns = ['title', 'author', 'isbn', 'thumbnail']
        values = [
            data.bookTitle, 
            data.bookAuthor, 
            book_isbn,
            data.bookThumbnail,
            ]
        insert_into_db(columns, values, 'books')

    book_id = get_book_id_by_isbn(book_isbn)[0]
    # save review
    columns = ['review', 'date_read', 'book_reviewed', 'user_id']
    values = [data.review, data.date_read, book_id, data.reviewed_by]
    insert_into_db(columns, values, 'reviews')

    return {'status': 'success', 'message': 'Review saved successfully'}


@app.put('/edit_review')
def edit_review(review_id: str = Body(...),
                review_text: str = Body(...)):
    
    update_data(table = 'reviews',
                column = 'review',
                value = review_text,
                condition = 'review_id',
                condition_value = review_id
                )
    
    return {'status': 'success', 'message': 'Review edited successfully'}


@app.delete('/delete_review')
def delete_review(review_id: str):
    delete_row(table='reviews',
               column='review_id',
               value=review_id)
    return {'status': 'success', 'message': 'Review deleted successfully'}


@app.get('/get_user')
def get_user(id: str = Form(...)):
    user_data = get_user_data(id)
    return {'detail':'Login successful', 'data': {'user_data': user_data}}


@app.put('/like')
def like_review(user_id: str, review_id: str):
    is_liked = check_if_exists(
        columns= 'like_id',
        table= 'review_likes',
        condition1= 'user_id',
        value1= user_id,
        condition2= 'review_id',
        value2= review_id
    ) != None

    response = save_like_to_db(user_id, review_id, is_liked)
    return {'status': 'success', 'message': response}