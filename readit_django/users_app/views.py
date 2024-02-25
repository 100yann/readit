from django.shortcuts import render, redirect
import requests


def register_user(request, method=['GET', 'POST']):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')

        response = requests.post('http://127.0.0.1:3000/save_user', data = {
            'email': user_email,
            'password': user_password,
            'first_name': first_name,
            'last_name': last_name
        })

        if response.status_code == 200:
            response_data = response.json()
            user_id = response_data['data']['user_id']

            request.session['user'] = user_id
            request.session['user_email'] = user_email

            return redirect('/home')
        
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

            user_id = response_data['data'][3]

            request.session['user'] = user_id
            request.session['user_name'] = response_data['data'][0]

            return redirect('/home')

    return render(request, 'users/login.html')


def logout_user(request):
    request.session['user'] = ''
    request.session['user_email'] = ''
    return redirect('/home')


def display_user_profile(request, user_id):
    response = requests.get(f'http://127.0.0.1:3000/user/{user_id}')

    if response.status_code == 200:
        response_data = response.json()
        user = response_data[0][0]
        reviews = response_data[1]
        
        print(user, reviews, sep='\n\n')
        return render(request, 'users/user_profile.html', 
                      context = {
                          'user': user,
                          'reviews': reviews
                      })