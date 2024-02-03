from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_page, name='home_page'),
    path("new", views.new_review, name='new_review'),
    path('find/<str:book_title>', views.find_book, name='find_book'),
    path('book/<str:isbn>', views.display_book, name='display_book')
] 