from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'pitle/index.html')

def signIn(request):
    return render(request, 'pitle/login-password.html')
