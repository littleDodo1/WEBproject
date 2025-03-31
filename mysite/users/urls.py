from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('login/', views.logIn, name='login'),
    path('register/', views.signIn, name='register'),
]
