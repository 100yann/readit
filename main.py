import requests
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import insert_into_db, get_reviews

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
    posts = get_reviews()
    return templates.TemplateResponse("index.html", 
    {
        "request": request, 
        "posts": posts
        })


@app.get("/find")
def search_results(request: Request, search: str = Query(..., title="Search")):
    search_values = search
    results = search_books(search_values)
    return format_results(results)


@app.get("/author")
def author(author: str = Query(..., title="Author")):
    return search_authors(author)


@app.get("/new_review")
def new_review(request: Request):
    return templates.TemplateResponse("add_review.html", {
        'request': request
    })

@app.get("/save_review")
def save_post(
    request: Request, 
    review_content: str = Query(..., title="Review"),
    date_read: str = Query(..., title="Date"),
    isbn: str = Query(..., title="ISBN")
):  
    print(type(date_read))
    print(review_content, date_read, isbn)
    # columns = ['review_content', 'date_read', 'isbn']
    # data = [review_content, date_read, isbn]

    # insert_into_db(columns, data, 'reviews')
    return 'success'