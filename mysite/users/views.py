from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegisterForm

from .models import *


def index(request):
    return render(request, 'users/index.html')


def AboutUs(request):
    return render(request, 'users/info_about_us.html')

def profile_view(request):
    return render(request, 'users/profile.html')


class RegisterUser(CreateView):
    form_class = RegisterForm
    template_name = 'users/register.html'

    def get_success_url(self):
        redirect_to = self.request.GET.get("next") or "/"
        return f'/login/?next={redirect_to}'


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'users/login-password.html'

    def get_success_url(self):
        redirect_to = self.request.POST.get("next", "/")
        return redirect_to
