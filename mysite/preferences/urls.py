from django.urls import path
from . import views

urlpatterns = [
    path('preferences/', views.edit_preferences, name='edit_preferences'),
]