from django.shortcuts import render

# Create your views here.
def new_review(request, method=['GET', 'POST']):
    return render(request, 'new_review.html')


def home_page(request):
    return render(request, 'index.html')