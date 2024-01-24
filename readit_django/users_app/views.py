from django.shortcuts import render
import requests

def register(request, method=['GET', 'POST']):
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


def login(request, method=['GET', 'POST']):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')  

        response = requests.post('http://127.0.0.1:3000/authenticate_user/', data = {
            'email': user_email,
            'password': user_password
        })

        print(response.status_code)
        print(response.json())
    return render(request, "users/login.html")