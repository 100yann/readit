from django.shortcuts import render, redirect
from django.urls import reverse
from .utils import *
from django.http import JsonResponse, HttpResponse
import json
import requests
from requests.exceptions import ConnectionError
from django.conf import settings


def home_page(request):

    try:
        response = requests.get(f'{settings.FASTAPI_URL}/reviews/recent')
    except ConnectionError:
        return render(request, 'error.html')
    
    reviews = response.json()

    return render(request, 'index.html', context={
        'reviews': reviews
    })


def new_review(request, method=['GET', 'POST']):
    jwt_token = request.COOKIES.get('access_token')
    if not jwt_token:
        return redirect('login')
        
    if request.method == 'POST':
        data = json.loads(request.body)
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.post(f'{settings.FASTAPI_URL}/reviews/', json={'review': data['review'], 'book': data['book']}, headers=headers)
        
        response_data = response.json()
        return JsonResponse(data = response_data, status = response.status_code)
    else:
        return render(request, 'new_review.html')


def edit_review(request, review_id, method=['PUT']):
    review_text = json.loads(request.body)
    response = requests.put(f'{settings.FASTAPI_URL}/edit_review', 
                            json={'review_id': review_id, 'review_text': review_text})

    return HttpResponse()


def delete_review(request, review_id, method=['DELETE']):
    response = requests.delete(f'{settings.FASTAPI_URL}/delete_review', params={'review_id': review_id})
    return HttpResponse()


def like_review(request, review_id, method=['PUT']):
    user_id = request.session['user']
    response = requests.put(f'{settings.FASTAPI_URL}/like', params={'user_id': user_id, 
                                                           'review_id': review_id})
    review_status = response.json()['message']
    return JsonResponse({'status': review_status})


def find_book(request, book_title):
    results = get_books_by_title(title = book_title)
    formatted_results = format_results(results)
    return JsonResponse(formatted_results, safe=False)


def display_book(request, isbn): 
    user_id = request.session['id']

    # get more data for the opened book through Google API using ISBN as book identfier
    book_details = get_book_by_isbn(isbn)

    # get all reviews for this book
    response = requests.get(f'{settings.FASTAPI_URL}/book/get/{isbn}', params={
        'user_id': user_id,
        })
    
    if response.status_code == 200:
        data = response.json()
        if data['shelf']:
            bookshelf = data['shelf'][0]
        else:
            bookshelf = ''
            
    return render(request, 'display_book.html', 
                context={
                    'details': book_details, 
                    'reviews': data['reviews'],
                    'user_rating': data['rating'],
                    'bookshelf': bookshelf,
                    'isbn': isbn
                    })


def save_book_to_bookshelf(request, method=['POST']):
    jwt_token = request.COOKIES.get('access_token')
    if not jwt_token:
        return redirect('login')

    data = json.loads(request.body)
    book_isbn = data['isbn']
    bookshelf = data['bookshelf']
    
    print(book_isbn, bookshelf)
    headers = {'Authorization': f'Bearer {jwt_token}'}
    payload = {'shelf': bookshelf}
    response = requests.post(f'{settings.FASTAPI_URL}/book/shelve/{book_isbn}', 
                            json=payload,
                            headers=headers
                            )
    print(response)
    return HttpResponse()

def search_for_book(request, method=['GET']):
    book_search = request.GET.get('book')

    response = requests.get(f'{settings.FASTAPI_URL}/book/find/{book_search}')
    results = response.json()
    
    return render(request, 'search_results.html', context = {
        'books': results
    })