from django.urls import path
from . import views

urlpatterns = [
    path('edit/', views.edit_preferences, name='edit_preferences'),
    path('profile/', views.profile_view, name = 'profile_view'),
    path('', views.view_preferences, name='view_preferences'),
]