from django.shortcuts import render
from .utils import *
from django.http import JsonResponse



# Create your views here.
def new_review(request, method=['GET', 'POST']):
    return render(request, 'new_review.html')


def home_page(request):
    return render(request, 'index.html')


def find_book(request, book_title):
    results = get_books_by_title(title = book_title)
    formatted_results = format_results(results)
    return JsonResponse(formatted_results, safe=False)