from django.shortcuts import render
from .utils import *
from django.http import JsonResponse
import json
import requests

FASTAPI_URL = 'http://127.0.0.1:3000'

# Create your views here.
def home_page(request):
    response = requests.get(f'{FASTAPI_URL}/get_reviews')
    data = response.json()
    reviews = data.get('reviews', [])

    for review in reviews:
        book_isbn = review['book_reviewed']
        book_info = get_book_by_isbn(book_isbn, preview=True)
        for key in book_info.keys():
            review[key] = book_info[key]
    
    return render(request, 'index.html', context={
        'reviews': reviews
    })


def new_review(request, method=['GET', 'POST']):
    if request.method == 'POST':
        data = json.loads(request.body)
        data['reviewed_by'] = int(request.session['user'])

        response = requests.post(f'{FASTAPI_URL}/save_review', json=data)

    return render(request, 'new_review.html')


def find_book(request, book_title):
    results = get_books_by_title(title = book_title)
    formatted_results = format_results(results)
    return JsonResponse(formatted_results, safe=False)


def display_book(request, isbn):
    book_details = get_book_by_isbn(isbn)
    return render(request, 'display_book.html', context={'details': book_details})