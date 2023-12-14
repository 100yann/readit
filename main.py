import requests
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


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