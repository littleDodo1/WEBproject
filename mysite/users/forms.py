from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ваше имя'}))
    email = forms.CharField(label='email', widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Email'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Пароль'}))
    password2 = forms.CharField(label='Пароль2', widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Повторите пароль'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        