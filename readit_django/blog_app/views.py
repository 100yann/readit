from django.shortcuts import render, redirect
from django.urls import reverse
from .utils import *
from django.http import JsonResponse, HttpResponse
import json
import requests

FASTAPI_URL = 'http://127.0.0.1:3000'


def home_page(request):
    response = requests.get(f'{FASTAPI_URL}/get_reviews')
    data = response.json()
    reviews = data.get('reviews', [])

    return render(request, 'index.html', context={
        'reviews': reviews
    })

def new_review(request, method=['GET', 'POST']):
    if request.method == 'POST':
        data = json.loads(request.body)
        data['reviewed_by'] = int(request.session['user'])
        response = requests.post(f'{FASTAPI_URL}/save_review', json=data)
        return HttpResponse()
    else:
        return render(request, 'new_review.html')


def edit_review(request, review_id, method=['PUT']):
    review_text = json.loads(request.body)
    response = requests.put(f'{FASTAPI_URL}/edit_review', 
                            json={'review_id': review_id, 'review_text': review_text})


    return HttpResponse()


def delete_review(request, review_id, method=['DELETE']):
    response = requests.delete(f'{FASTAPI_URL}/delete_review', params={'review_id': review_id})
    return HttpResponse()

def find_book(request, book_title):
    results = get_books_by_title(title = book_title)
    formatted_results = format_results(results)
    return JsonResponse(formatted_results, safe=False)


def display_book(request, isbn):
    book_details = get_book_by_isbn(isbn)

    response = requests.get(f'{FASTAPI_URL}/get_reviews', params={'isbn': isbn})
    data = response.json()
    reviews = data.get('reviews', [])


    return render(request, 'display_book.html', context={'details': book_details, 'reviews': reviews})