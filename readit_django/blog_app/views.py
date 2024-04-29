from django.shortcuts import render, redirect
from django.urls import reverse
from .utils import *
from django.http import JsonResponse, HttpResponse, HttpResponseServerError
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
    # book_details = get_book_by_isbn(isbn)
    
    # avoid querying google api while working on the frontend
    book_details = {'title': 'Slaughterhouse-Five', 'thumbnail': 'http://books.google.com/books/content?id=FM4y7N1kM9AC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api', 'author': 'Kurt Vonnegut', 'subtitle': 'A Novel; 50th anniversary edition', 'publisher': 'Dial Press', 'publishedDate': '2009-08-11', 'description': 'A special fiftieth anniversary edition of Kurt Vonnegut’s masterpiece, “a desperate, painfully honest attempt to confront the monstrous crimes of the twentieth century” (Time), featuring a new introduction by Kevin Powers, author of the National Book Award finalist The Yellow Birds Selected by the Modern Library as one of the 100 best novels of all time Slaughterhouse-Five, an American classic, is one of the world’s great antiwar books. Centering on the infamous World War II firebombing of Dresden, the novel is the result of what Kurt Vonnegut described as a twenty-three-year struggle to write a book about what he had witnessed as an American prisoner of war. It combines historical fiction, science fiction, autobiography, and satire in an account of the life of Billy Pilgrim, a barber’s son turned draftee turned optometrist turned alien abductee. As Vonnegut had, Billy experiences the destruction of Dresden as a POW. Unlike Vonnegut, he experiences time travel, or coming “unstuck in time.” An instant bestseller, Slaughterhouse-Five made Kurt Vonnegut a cult hero in American literature, a reputation that only strengthened over time, despite his being banned and censored by some libraries and schools for content and language. But it was precisely those elements of Vonnegut’s writing—the political edginess, the genre-bending inventiveness, the frank violence, the transgressive wit—that have inspired generations of readers not just to look differently at the world around them but to find the confidence to say something about it. Authors as wide-ranging as Norman Mailer, John Irving, Michael Crichton, Tim O’Brien, Margaret Atwood, Elizabeth Strout, David Sedaris, Jennifer Egan, and J. K. Rowling have all found inspiration in Vonnegut’s words. Jonathan Safran Foer has described Vonnegut as “the kind of writer who made people—young people especially—want to write.” George Saunders has declared Vonnegut to be “the great, urgent, passionate American writer of our century, who offers us . . . a model of the kind of compassionate thinking that might yet save us from ourselves.” More than fifty years after its initial publication at the height of the Vietnam War, Vonnegut’s portrayal of political disillusionment, PTSD, and postwar anxiety feels as relevant, darkly humorous, and profoundly affecting as ever, an enduring beacon through our own era’s uncertainties.', 'pageCount': 286, 'categories': ['Fiction']}

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
                    'isbn': isbn,
                    'book_id': data['book_id']
                    })


def save_book_to_bookshelf(request, method=['POST']):
    jwt_token = request.COOKIES.get('access_token')
    if not jwt_token:
        return redirect('login')

    data = json.loads(request.body)
    book_isbn = data['isbn']
    bookshelf = data['bookshelf']
    
    headers = {'Authorization': f'Bearer {jwt_token}'}
    payload = {'shelf': bookshelf}
    response = requests.post(f'{settings.FASTAPI_URL}/book/shelve/{book_isbn}', 
                            json=payload,
                            headers=headers
                            )

    if response.status_code != 201 and response.status_code != 204:
        return HttpResponseServerError()
    
    return HttpResponse(status=response.status_code)


def rate_book(request, method=['POST']):
    jwt_token = request.COOKIES.get('access_token')
    if not jwt_token:
        return redirect('login')

    data = json.loads(request.body)
    book_id = data['book_id']
    rating = data['rating']

    headers = {'Authorization': f'Bearer {jwt_token}'}
    response = requests.post(f'{settings.FASTAPI_URL}/book/rate/{book_id}', 
                             json={'rating': rating}, 
                             headers=headers
                             )
    return HttpResponse()


def search_for_book(request, method=['GET']):
    book_search = request.GET.get('book')

    response = requests.get(f'{settings.FASTAPI_URL}/book/find/{book_search}')
    results = response.json()
    
    return render(request, 'search_results.html', context = {
        'books': results
    })