from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_preferences, name='view_preferences'),
    path('edit/', views.edit_preferences, name='edit_preferences'),
    path('recommendations_books/', views.recommendations_books, name='recommendations_books'),
    path('recommendations_movies/', views.recommendations_movies, name='recommendations_movies'),
    path('profile/', views.profile_view, name='profile')
]