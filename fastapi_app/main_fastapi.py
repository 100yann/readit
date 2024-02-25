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

        if user_id and isbn:
            book_id = get_book_id_by_isbn(isbn)[0]
            rating = get_data('ratings', columns = ['rating'], **{'user_id': user_id, 'book_id': book_id})
            bookshelf = get_data('bookshelves', columns = ['shelf'], **{'user_id': user_id, 'book_id': book_id})
            
            return {'reviews': reviews, 'rating': rating, 'bookshelf': bookshelf}
        
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
        user_data = get_user_data(user_id)
        return {'detail':'Login successful', 'data': user_data}
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

    # check if a book has already been saved in the 'read' bookshelf
    conditions = {
        'user_id': data.reviewed_by,
        'book_id': book_id,
        'shelf': 'read'
    }

    is_book_read = get_data(
        table='bookshelves',
        columns=['shelf_id'],
        **conditions
    )

    # save the book to the 'read' bookshelf
    if not is_book_read:
        columns = ['user_id', 'book_id', 'shelf']
        values = [data.reviewed_by, book_id, 'read']
        insert_into_db(columns, values, 'bookshelves')

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


class RateRequest(BaseModel):
    user_id: int
    isbn: str
    action: str
    rating: int

@app.post('/rate')
def rate_book(rate_request: RateRequest):
    # get the book_id by using its isbn
    book_id = get_book_id_by_isbn(rate_request.isbn)[0]

    # check if the book has already been rated by this user
    is_rated = check_if_exists(
        columns = 'rating_id',
        table = 'ratings',
        condition1 = 'user_id',
        value1 = rate_request.user_id,
        condition2 = 'book_id',
        value2 = book_id
    )

    # if the book has been rated update the existing rating
    if is_rated != None:
        rating_id = is_rated[0] # since cursor.fetchone() returns a tuple
        update_data(
            table = 'ratings',
            column = 'rating',
            value = rate_request.rating,
            condition = 'rating_id', 
            condition_value = rating_id
        )

    # create an entry of the rating if it hasn't been rated by the user yet
    else:
        columns = ['book_id', 'user_id', 'rating']
        values = [book_id, rate_request.user_id, rate_request.rating]
        insert_into_db(
            columns,
            values,
            table = 'ratings'
        )

    return {'status': 'success', 'message': 'Rating updated successfully'}


class SaveRequest(BaseModel):
    user_id: int
    isbn: str
    action: str


@app.post('/save')
def save_book(save_request: SaveRequest):
    book_id = get_book_id_by_isbn(save_request.isbn)[0]

    if save_request.action == 'save_book':

        columns = ['user_id', 'book_id']
        values = [save_request.user_id, book_id]

        insert_into_db(
            columns,
            values,
            table = 'bookshelves'
        )

        message = 'Book saved successfully' 

    else:
        shelved_book_id = get_data(
            'bookshelves', 
            columns= ['shelf_id'],
            **{'user_id': save_request.user_id, 'book_id': book_id},
        )[0][0]

        delete_row(
            table = 'bookshelves',
            column = 'shelf_id',
            value = shelved_book_id
        )
        
        message = 'Book removed successfully'
    return {'status': 'success', 'message': message}


@app.get('/user/{profile_id}')
def get_user_profile(profile_id):
    # get user's data
    user_data = get_data(
        table = 'users',
        columns = ['id', 'email', 'first_name', 'last_name'],
        **{'id': profile_id}
    )

    # get all the books the user has read
    columns = ['bookshelves.*', 'books.*']
    join_clauses = [{
        'type': 'LEFT',
        'table': 'books',
        'col1': 'bookshelves.book_id',
        'col2': 'books.book_id'
    }]

    conditions = {
        'join_clauses': join_clauses, 
        'bookshelves.user_id': profile_id
    }
    books_read = get_data(
        table = 'bookshelves',
        columns = columns,
        **conditions
    )

    # get all the books the user has reviewed
    columns = ['reviews.*', 'books.*']
    join_clauses = [{
        'type': 'LEFT', 
        'table': 'books', 
        'col1': 'reviews.book_reviewed', 
        'col2': 'books.book_id'
        },
        ]
   
    conditions = {'join_clauses': join_clauses, 
                  'reviews.user_id': profile_id
                  }
    
    reviews = get_data(
        table = 'reviews',
        columns = columns,
        **conditions
    )
    return user_data, books_read, reviews


if __name__ == '__main__':
    ...