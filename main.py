import requests
from fastapi import FastAPI, Request, Query, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import *
from users import *
from pydantic import BaseModel



class ReviewData(BaseModel):
    bookIsbn: str
    bookTitle: str
    bookAuthor: str
    bookDescription: str
    bookThumbnail: str
    review: str
    date_read: str


def search_authors(author=str):
    formatted_author = author.strip().replace(' ', '+')
    base_url = f'https://www.googleapis.com/books/v1/volumes'
    params = {
        'q': f'inauthor:{formatted_author}'
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])
    else:
        return None


def search_books(title):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': title
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])
    else:
        return response.status_code
    return None


def format_results(results):
    formatted_results = []
    for result in results:
        if 'volumeInfo' in result and 'imageLinks' in result['volumeInfo']:
            formatted_results.append({
                'title': result['volumeInfo']['title'],
                'author': result['volumeInfo']['authors'],
                'thumbnail': result['volumeInfo']['imageLinks']['thumbnail'],
                'publisher': result['volumeInfo']['publisher'],
                'description': result['volumeInfo']['description'],
                'pageCount': result['volumeInfo']['pageCount'],
                'categories': result['volumeInfo']['categories'],
                'isbn': result['volumeInfo']['industryIdentifiers'][0]['identifier']
            })
    return formatted_results


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="static")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", 
    {
        "request": request, 
        })


@app.get("/sign_up")
def sign_up(request: Request):
    return templates.TemplateResponse("/users/sign_up.html",
    {
        "request": request,
    })


@app.post("/sign_up")
def post_sign_up(
    request: Request, 
    email: str = Body(..., title="email"), 
    password: str = Body(..., title="password")
    ):
    email = email
    password = hash_password(password)
    print(email, password)
    return JSONResponse(content={"status": "success", "message": "Review saved successfully"})


@app.get("/find")
def search_results(request: Request, search: str = Query(..., title="Search")):
    search_values = search
    results = search_books(search_values)
    return format_results(results)


@app.get("/author")
def author(author: str = Query(..., title="Author")):
    return search_authors(author)


@app.get("/get_reviews")
def get_existing_reviews():
    return get_reviews()

@app.get("/new_review")
def new_review(request: Request):
    return templates.TemplateResponse("add_review.html", {
        'request': request
    })

@app.post("/save_review")
def save_review(request: Request, data: ReviewData):  
    book_isbn = data.bookIsbn

    # Save book to DB if it's not already saved
    if not check_existing(1, 'book_details', 'isbn', book_isbn):
        columns = ['title', 'author', 'description', 'isbn', 'thumbnail']
        data = [
            data.bookTitle, 
            data.bookAuthor, 
            data.bookDescription,
            book_isbn,
            data.bookThumbnail,
            ]
        insert_into_db(columns, data, 'book_details')
    else:
        ...

    # Get the id of the book reviewed
    book_id = get_book_id_by_isbn(book_isbn)[0]

    # save review
    columns = ['review_content', 'date_read', 'book_reviewed']
    data = [data.review, data.date_read, book_id]
    insert_into_db(columns, data, 'reviews')

    return JSONResponse(content={"status": "success", "message": "Review saved successfully"})
