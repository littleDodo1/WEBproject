from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'users/index.html')

def logIn(request):
    return render(request, 'users/login-password.html')

def signIn(request):
    return render(request, 'users/register.html')
