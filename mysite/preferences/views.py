from django.shortcuts import render, redirect
from .forms import PreferenceForm
from .models import Preference
from django.contrib.auth.decorators import login_required
import requests
import urllib3
import uuid
'''from dotenv import load_dotenv
import os

load_dotenv()'''

@login_required
def edit_preferences(request):
    try:
        preference = Preference.objects.get(user=request.user)
    except Preference.DoesNotExist:
        preference = Preference(user=request.user)
        preference.save()

    if request.method == "POST":
        form = PreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = PreferenceForm(instance=preference)

    return render(request, 'preferences/edit_preferences.html', {'form': form})


@login_required
def view_preferences(request):
    try:
        preference = Preference.objects.get(user=request.user)
    except Preference.DoesNotExist:
        preference = None

    return render(request, 'preferences/view_preferences.html', {'preference': preference})

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_access_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {'scope': 'GIGACHAT_API_PERS'}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f"Basic {os.getenv('API_AUTH_TOKEN')}"  # Токен
    }

    response = requests.post(url, headers=headers, data=payload, verify=False)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        return None

def ask_gigachat(prompt, access_token):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    json_data = {
        "model": "GigaChat:latest",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=json_data, verify=False)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    return "Oops, нейросеть не смогла найти ответ..."

@login_required
def recommendations_movies(request):
    try:
        preference = Preference.objects.get(user=request.user)
    except Preference.DoesNotExist:
        preference = None

    recommendations_movies = None

    if preference:
        preferences_data = {
            'movie_genres': [genre.name for genre in preference.favorite_movie_genres.all()],
            'countries': [country.name for country in preference.favorite_countries.all()],
            'movie_decades': [decade.name for decade in preference.favorite_movie_decades.all()],
            'movie_directors': [director.name for director in preference.favorite_movie_directors.all()],
        }

        access_token = get_access_token()
        if access_token:
            prompt_movies = (
                "Ты — помощник по подбору фильмов.\n\n"
                "На основе предпочтений пользователя:\n"
                f"Жанры фильмов: {', '.join(preferences_data.get('movie_genres', []))}\n"
                f"Любимые страны: {', '.join(preferences_data.get('countries', []))}\n"
                f"Десятилетия фильмов: {', '.join(preferences_data.get('movie_decades', []))}\n"
                f"Любимые режиссёры: {', '.join(preferences_data.get('movie_directors', []))}\n\n"
                "Порекомендуй 10 фильмов.\n"
                "Просто напиши список фильмов в формате:\n"
                "1. Название фильма — Режиссёр\n"
                "Без комментариев и пояснений."
            )
            recommendations_movies = ask_gigachat(prompt_movies, access_token)
        else:
            recommendations_movies = "Токен не получен"

    return render(request, 'preferences/recommendations_movies.html', {
        'recommendations_movies': recommendations_movies,
        'preference': preference,
    })

@login_required
def recommendations_books(request):
    try:
        preference = Preference.objects.get(user=request.user)
    except Preference.DoesNotExist:
        preference = None

    recommendations_books = None

    if preference:
        preferences_data = {
            'book_genres': [genre.name for genre in preference.favorite_book_genres.all()],
            'countries': [country.name for country in preference.favorite_countries.all()],
            'book_decades': [decade.name for decade in preference.favorite_book_decades.all()],
            'book_authors': [author.name for author in preference.favorite_book_authors.all()],
        }

        access_token = get_access_token()
        if access_token:
            prompt_books = (
                "Ты — помощник по подбору книг.\n\n"
                "На основе предпочтений пользователя:\n"
                f"Жанры книг: {', '.join(preferences_data.get('book_genres', []))}\n"
                f"Любимые страны: {', '.join(preferences_data.get('countries', []))}\n"
                f"Десятилетия книг: {', '.join(preferences_data.get('book_decades', []))}\n"
                f"Любимые авторы: {', '.join(preferences_data.get('book_authors', []))}\n\n"
                "Порекомендуй 10 книг.\n"
                "Просто напиши список книг в формате:\n"
                "1. Название книги — Автор\n"
                "Без комментариев и пояснений."
            )
            recommendations_books = ask_gigachat(prompt_books, access_token)
        else:
            recommendations_books = "Токен не получен"

    return render(request, 'preferences/recommendations_books.html', {
        'recommendations_books': recommendations_books,
        'preference': preference,
    })