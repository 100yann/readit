from django.urls import path, re_path
from django.views.generic.base import RedirectView
from . import views


urlpatterns = [
    path('home', views.home_page, name='home_page'),
    path("new", views.new_review, name='new_review'),
    path('find/<str:book_title>', views.find_book, name='find_book'),
    path('book/<str:isbn>', views.display_book, name='display_book'),
    path('edit/<str:review_id>', views.edit_review, name='edit_review'),
    path('delete/<str:review_id>', views.delete_review, name='delete_review'),
    re_path(r'^.*$', RedirectView.as_view(url='home', permanent=False), name='index')
] 