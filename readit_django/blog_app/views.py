from django.shortcuts import render, redirect
from django.urls import reverse
from .utils import *
from django.http import JsonResponse, HttpResponse
import json
import requests
from requests.exceptions import ConnectionError
from django.conf import settings


FASTAPI_URL = 'http://127.0.0.1:3000'


def home_page(request):

    try:
        response = requests.get(f'{settings.FASTAPI_URL}/reviews/recent')
    except ConnectionError:
        return render(request, 'error.html')
    
    
    reviews = response.json()
    print(reviews)

    return render(request, 'index.html', context={
        'reviews': reviews
    })


def new_review(request, method=['GET', 'POST']):
    if not request.session['id']:
        return redirect('login')
    
    if request.method == 'POST':
        data = json.loads(request.body)
        jwt_token = request.COOKIES.get('access_token')
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.post(f'{FASTAPI_URL}/reviews/', json={'review': data['review'], 'book': data['book']}, headers=headers)
        
        response_data = response.json()
        return JsonResponse(data = response_data, status = response.status_code)
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


def like_review(request, review_id, method=['PUT']):
    user_id = request.session['user']
    response = requests.put(f'{FASTAPI_URL}/like', params={'user_id': user_id, 
                                                           'review_id': review_id})
    review_status = response.json()['message']
    return JsonResponse({'status': review_status})


def find_book(request, book_title):
    results = get_books_by_title(title = book_title)
    formatted_results = format_results(results)
    return JsonResponse(formatted_results, safe=False)


def display_book(request, isbn):
    user_id = request.session['user']
    
    if request.method == 'GET':
        # get more data for the opened book through Google API using ISBN as book identfier
        book_details = get_book_by_isbn(isbn)

        # get all reviews for this book
        response = requests.get(f'{FASTAPI_URL}/get_reviews', params={
            'isbn': isbn, 
            'user_id': user_id,
            })
        
        data = response.json()
        reviews = data.get('reviews', [])
        rating = data.get('rating', '')[0][0] if data.get('rating') else ''
        bookshelf = data.get('bookshelf', '')[0][0] if data.get('bookshelf') else ''

        return render(request, 'display_book.html', 
                    context={
                        'details': book_details, 
                        'reviews': reviews,
                        'isbn': isbn,
                        'user_rating': rating,
                        'bookshelf': bookshelf
                        })

    # else the request is POST
    data = json.loads(request.body)
    action = data['action']

    response_json = {
        'user_id': user_id,
        'isbn': isbn,
        'action': action
    }
    
    if action in ['save_book', 'remove_book']:
        response = requests.post(f'{FASTAPI_URL}/save', json=response_json)

    elif action == 'rate':
        response_json['rating'] = data['rating']

        response = requests.post(f'{FASTAPI_URL}/rate', json=response_json)
        return HttpResponse()


    return HttpResponse()
