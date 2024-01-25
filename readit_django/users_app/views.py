from django.shortcuts import render
from django.contrib.auth import login, authenticate
import requests


def register_user(request, method=['GET', 'POST']):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')

        response = requests.post('http://127.0.0.1:3000/save_user/', data = {
            'email': user_email,
            'password': user_password
        })

        print(response.status_code)
        print(response.json())
    return render(request, "users/register.html")


def login_user(request, method=['GET', 'POST']):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')  

        response = requests.post('http://127.0.0.1:3000/authenticate_user/', data = {
            'email': user_email,
            'password': user_password
        })
        if response.status_code == 200:
            response_data = response.json()
            user_id = response_data['data']['user_id']

            request.session['user'] = user_id
            request.session['user_email'] = user_email

            return render(request, "users/login.html")

    return render(request, "users/login.html")


def logout_user(request):
    request.session['user'] = ''
    request.session['user_email'] = ''
    return render(request, "users/login.html")

