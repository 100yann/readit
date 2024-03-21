import requests
from .database import get_db
from . import models
from sqlalchemy.orm import Session


def save_book_to_bookshelf(user_id, book_id, bookshelf, db: Session):
    bookshelf_entry = models.Bookshelves(book_id=book_id, 
                                         user_shelved=int(user_id), 
                                         bookshelf=bookshelf
                                         )
    db.add(bookshelf_entry)
    db.commit()
    db.refresh(bookshelf_entry)
    return bookshelf_entry


def get_books_by_title(title):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': title,
        'maxResults': 5 
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        results = format_results(data.get("items", []))
        return results
    else:
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

