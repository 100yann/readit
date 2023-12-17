import requests
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="static")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/find")
def search_results(request: Request, search: str = Query(..., title="Search")):
    search_values = search
    results = search_books(search_values)
    return results

@app.get("/author")
def author(author: str = Query(..., title="Author")):
    return search_authors(author)

@app.get("/post")
def new_post(request: Request, post: str = Query(..., title="Post")):
    print('post')
    return 'success'