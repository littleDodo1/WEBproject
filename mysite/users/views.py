from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')

def logIn(request):
    return render(request, 'login-password.html')

def signIn(request, DataMi):
    return render(request, 'register.html')
