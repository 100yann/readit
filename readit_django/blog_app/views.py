from django.shortcuts import render
from .utils import *
from django.http import JsonResponse
import json
import requests


# Create your views here.
def home_page(request):
    return render(request, 'index.html')


def new_review(request, method=['GET', 'POST']):
    if request.method == 'POST':
        data = json.loads(request.body)
        data['reviewed_by'] = int(request.session['user'])
        print(data)
        response = requests.post('http://127.0.0.1:3000/save_review', json=data)

    return render(request, 'new_review.html')


def find_book(request, book_title):
    results = get_books_by_title(title = book_title)
    formatted_results = format_results(results)
    return JsonResponse(formatted_results, safe=False)