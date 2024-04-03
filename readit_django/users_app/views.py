from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
import requests
from django.conf import settings


def register_user(request, method=['GET', 'POST']):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')

        response = requests.post(f'{settings.FASTAPI_URL}/users/create', json = {
            'email': user_email,
            'password': user_password,
            'first_name': first_name,
            'last_name': last_name 
        })
 
        response_data = response.json()
        return JsonResponse(response_data, status=response.status_code)

    return render(request, "users/register.html")


def login_user(request, method=['GET', 'POST']):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')  

        data = {
            'username': user_email,
            'password': user_password,
        }

        response = requests.post(f'{settings.FASTAPI_URL}/users/login', 
                                 data=data
                                 )
        response_data = response.json()

        user_name = response_data['name']
        user_id = response_data['id']

        request.session['name'] = user_name
        request.session['id'] = user_id
                
        response = JsonResponse({'message': 'Login successful'})
        response.set_cookie(key='access_token', value=response_data['access_token'], httponly=True)
        return response
    
    return render(request, 'users/login.html')


def logout_user(request):
    response = redirect('/home')
    response.delete_cookie('access_token')

    request.session['name'] = ''
    request.session['id'] = ''
    return response


def display_user_profile(request, user_id):
    response = requests.get(f'http://127.0.0.1:3000/user/{user_id}')

    if response.status_code == 200:
        response_data = response.json()
        user = response_data[0][0]
        books_read = response_data[1]
        reviews = response_data[2]

        return render(request, 'users/user_profile.html', 
                      context = {
                          'user': user,
                          'books_read': books_read,
                          'reviews': reviews
                      })