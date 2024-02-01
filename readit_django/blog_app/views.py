from django.shortcuts import render
from .utils import *
from django.http import JsonResponse
import json
import requests

FASTAPI_URL = 'http://127.0.0.1:3000'

# Create your views here.
def home_page(request):
    # response = requests.get(f'{FASTAPI_URL}/get_reviews')
    # data = response.json()
    # reviews = data.get('reviews', [])    
    # print(reviews)
    dummy_data = [[18, 'This is a review', '2023-12-29T12:10:51.411983', '2023-12-28', 1, 8, 'Slaughterhouse-Five', 'Kurt Vonnegut', 'http://books.google.com/books/content?id=FM4y7N1kM9AC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api', 8, 'Stoyan', 'Kolev'], [19, 'awdasdsadasd', '2024-01-24T15:25:32.586629', '2024-01-15', 5, 8, 'Animal Farm', 'George Orwell', 'http://books.google.com/books/content?id=nkalO3OsoeMC&printsec=frontcover&img=1&zoom=1&source=gbs_api', 8, 'Stoyan', 'Kolev'], [20, 'asdasd', '2024-01-27T15:50:28.657327', '2024-01-09', 6, 8, 'All Quiet on the Western Front', 'Erich Maria Remarque', 'http://books.google.com/books/content?id=EDkU_EbrbmgC&printsec=frontcover&img=1&zoom=1&source=gbs_api', 8, 'Stoyan', 'Kolev']]
    return render(request, 'index.html', context = {'reviews': dummy_data})


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