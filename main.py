import requests
from fastapi import FastAPI, Request, Query, Body, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import *
from users import *
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware




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
    fields = ['title', 'authors', 'thumbnail', 'publisher', 'description', 'pageCount', 'categories', 'isbn']
    for result in results:
        if 'volumeInfo' in result and 'imageLinks' in result['volumeInfo']:
            curr = {}
            for field in fields:
                try:
                    if field == 'thumbnail':
                        curr[field] = result['volumeInfo']['imageLinks']['thumbnail']
                    elif field == 'isbn':
                        curr[field] = result['volumeInfo']['industryIdentifiers'][0]['identifier']
                    else:
                        curr[field] = result['volumeInfo'][field]
                except KeyError:
                    pass

            formatted_results.append(curr)
    return formatted_results


def create_session(request: Request, email):
    request.session['user'] = email

def get_current_user(request: Request):
    return request.session.get("user")

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
    # Get user email and hashed password
    email = email
    hashed_password = hash_password(password)
    # Save user
    if not save_user(email, hashed_password):
        return JSONResponse(content={"status": "error", "message": "Email already exists!"})

    return JSONResponse(content={"status": "success", "message": "Review saved successfully"})


@app.get('/sign_in')
def sign_in(request: Request):
    return templates.TemplateResponse('/users/sign_in.html', {"request": request})


@app.post('/sign_in')
def sign_in(
    request: Request, 
    email: str = Form(..., title="email"), 
    password: str = Form(..., title="password")
    ):

    # check if email exists in db
    if check_existing('password', 'users', 'email', email):
        # check if password is valid
        if verify_password(password, email):
            create_session(request, email)
            print(request.session)
        else:
            ...
    else: 
        ...
    return templates.TemplateResponse('/users/sign_in.html', {"request": request })


@app.get('/sign_out')
def sign_out(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")


@app.get("/get_user_id")
def get_user_id(request: Request):
    user_email = get_current_user(request)
    user_id = check_existing('id', 'users', 'email', user_email)[0]
    return user_id

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
def new_review(request: Request, current_user: str = Depends(get_current_user)):
    if current_user:
        return templates.TemplateResponse("add_review.html", {'request': request})
    else:
        return RedirectResponse(url='/sign_in')





@app.delete("/delete_review/{review_id}")
def delete_review(request: Request, review_id):
    delete_row(
        table='reviews',
        column='review_id',
        value=int(review_id))
    
    return JSONResponse(content={"status": "success", "message": "Review deleted successfully"})


# Save editted review
@app.put("/edit_review/{review_id}")
def edit_review(review_id, data: dict = Body(...)):
    update_data(
        table='reviews',
        column='review_content',
        value=data['text'],
        condition='review_id',
        condition_value = int(review_id)
    )
    return JSONResponse(content={"status": "success", "message": "Review editted successfully"})


app.add_middleware(SessionMiddleware, secret_key="some-random-string")
