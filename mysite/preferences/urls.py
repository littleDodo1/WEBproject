from django.urls import path
from . import views

urlpatterns = [
    path('edit/', views.edit_preferences, name='edit_preferences'),
    path('view/', views.view_preferences, name='view_preferences'),
]