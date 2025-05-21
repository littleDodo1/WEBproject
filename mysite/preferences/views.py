from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import PreferenceForm
from .models import Preference
from search.models import CachedBooks, CachedMovies
from django.contrib.auth.decorators import login_required
import requests, urllib3, uuid, os, re
from search.movie_api_utils import (
    fetch_kinopoisk_movie,
    get_cached_movie,
    cache_movie,
    cache_query,
    fetch_movie_search,
    sort_movies
)
from search.books_api_utils import (
    fetch_books_search,
    cache_book_query,
    sort_books,
    get_cached_book, fetch_single_book, cache_book
)
from dotenv import load_dotenv


load_dotenv()

@login_required(login_url='login')
def profile_view(request):
    return render(request, 'profile.html')

@login_required(login_url='login')
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

@login_required(login_url='login')
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

    response = requests.post(url, headers=headers, data=payload)
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

    response = requests.post(url, headers=headers, json=json_data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    return "Oops, нейросеть не смогла найти ответ..."
def attach_movies_to_recommendations(recommendations):
    for rec in recommendations:
        text = rec.get("text", "")
        match = re.search(r"[«\"](.+?)[»\"]", text)
        if match:
            title = match.group(1)
        else:
            title = text.split("—")[0].split("(")[0].strip()
            title = " ".join(title.split()[:3])

        #print(f"Название: {title}") #DEBUG

        search_results = fetch_movie_search(title, years="", country="", genres="")
        if search_results:
            movie_data = search_results[0]
            kp_id = movie_data.get('id')
            cached = get_cached_movie(kp_id)
            if cached:
                rec["movie"] = cached
                rec["movie_id"] = cached.get('id')
                #print(f"Найден в кеше {cached.get('name')}") #DEBUG
            else:
                full_data = fetch_kinopoisk_movie(kp_id)
                #print(f"полные данные\n{full_data}")
                if full_data:
                    cache_movie(full_data)
                    rec["movie"] = full_data
                    rec["movie_id"] = full_data.get('id')
                    #print(f"Найден через API и закэширован {full_data.get('name')}") #DEBUG
                else:
                    rec["movie"] = None
                    rec["movie_id"] = None
                    #print(f"Ошибка при получении данных по ID {kp_id}") #DEBUG
        else:
            rec["movie"] = None
            rec["movie_id"] = None
            #print(f"Не найден в кеше и API {title}") #DEBUG

    return recommendations
def attach_books_to_recommendations(recommendations):
    for rec in recommendations:
        text = rec.get("text", "")
        match = re.search(r'[«"](.+?)[»"]', text)
        if match:
            title = match.group(1)
        else:
            title = text.split("—")[0].split("(")[0].strip()
            title = " ".join(title.split()[:3])
        #print(title) #DEBUG
        #print(f"Поиск {title}") #DEBUG
        search_results = fetch_books_search(title, genres="")
        if search_results:
            api_book_data = search_results[0]
            key = api_book_data.get('key', '')

            book_data, content, substance = get_cached_book(key)

            if book_data:
                rec["book"] = book_data
                rec["summary"] = content
                rec["substance"] = substance
                key = book_data.get('key', '')
                if key.startswith('/works/'):
                    rec["book_key"] = key.replace('/works/', '')
                else:
                    rec["book_key"] = key
                #print(f"Найден в кеше {book_data.get('title')}") #DEBUG
            else:
                access_token = get_access_token()
                if access_token:
                    promptA = (
                        "Ты - помощник по генерации краткого содержания книг.\n\n"
                        "Напиши без каких либо комментариев, благодарения, вопросов от тебя 6 предложений о книге.\n"
                        "Мне нужно только описание без лишних слов, также учитывай что в названиях могут быть литературные слова\n"
                        f"Название книги: {title}"
                    )
                    summary = ask_gigachat(promptA, access_token)
                    promptB = (
                        "Ты - помощник по генерации содержания книг.\n\n"
                        "Напиши без каких либо комментариев, благодарения, вопросов от тебя 10-15 предложений о книге.\n"
                        f"Название книги: {title}"
                    )
                    substance = ask_gigachat(promptB, access_token)   
                else:
                    summary = ""
                    substance = ""  
                
                cache_book(api_book_data, content=summary, substance=substance)
                rec["book"] = api_book_data
                rec["summary"] = summary
                key = api_book_data.get('key', '')
                if key.startswith('/works/'):
                    rec["book_key"] = key.replace('/works/', '')
                else:
                    rec["book_key"] = key
                #print(f"Найден через API и закэширован {api_book_data.get('title')}") #DEBUG
        else:
            rec["book"] = None
            rec["summary"] = None
            rec["book_key"] = None
            rec["substance"] = None
            #print(f"Не найден в кеше и API {title}") #DEBUG
    #print(f"prefer   {substance}\n\n") #DEBUG
    return recommendations
@login_required(login_url='login')
def recommendations_movies(request):
    try:
        preference = Preference.objects.get(user=request.user)
    except Preference.DoesNotExist:
        return redirect('edit_preferences')
    
    if request.method == "POST":
        access_token = get_access_token()
        if access_token:
            preferences_data = {
                'movie_genres': [genre.name for genre in preference.favorite_movie_genres.all()],
                'countries': [country.name for country in preference.favorite_countries.all()],
                'movie_decades': [decade.name for decade in preference.favorite_movie_decades.all()],
                'movie_directors': [director.name for director in preference.favorite_movie_directors.all()],
            }

            prompt_movies = (
                "Ты — помощник по подбору фильмов.\n\n"
                "На основе предпочтений пользователя:\n"
                f"Жанры фильмов: {', '.join(preferences_data.get('movie_genres', []))}\n"
                f"Любимые страны: {', '.join(preferences_data.get('countries', []))}\n"
                f"Десятилетия фильмов: {', '.join(preferences_data.get('movie_decades', []))}\n"
                f"Любимые режиссёры: {', '.join(preferences_data.get('movie_directors', []))}\n"
                f"Также недавно пользователь смотрел:\n"
                f"Жанры: {', '.join(preference.last_viewed_movie_genres[-3:])}\n"
                f"Страны: {', '.join(preference.last_viewed_countries[-3:])}\n"
                f"Авторы: {', '.join(preference.last_viewed_directors[-3:])}\n\n"
                "Порекомендуй 10 фильмов.\n"
                "Просто напиши список фильмов в формате:\n"
                "1. Название фильма — Режиссёр\n"
                "Без комментариев и пояснений."
            )

            recommendations = ask_gigachat(prompt_movies, access_token)
            preference.saved_movie_recommendations = recommendations
            preference.movie_recommendations_updated = timezone.now()
            preference.save()
    recommendations_list = []
    if preference.saved_movie_recommendations:
        for line in preference.saved_movie_recommendations.splitlines():
            if line.strip():
                recommendations_list.append({'text': line.strip()})
        recommendations_list = attach_movies_to_recommendations(recommendations_list)
    return render(request, 'preferences/recommendations_movies.html', {
        'recommendations': recommendations_list,
        'preference': preference,
    })

@login_required(login_url='login')
def recommendations_books(request):
    try:
        preference = Preference.objects.get(user=request.user)
    except Preference.DoesNotExist:
        return redirect('edit_preferences')

    if request.method == "POST":
        access_token = get_access_token()
        if access_token:
            preferences_data = {
                'book_genres': [genre.name for genre in preference.favorite_book_genres.all()],
                'countries': [country.name for country in preference.favorite_countries.all()],
                'book_decades': [decade.name for decade in preference.favorite_book_decades.all()],
                'book_authors': [author.name for author in preference.favorite_book_authors.all()],
            }
            prompt_books = (
                "Ты — помощник по подбору книг.\n\n"
                "На основе предпочтений пользователя:\n"
                f"Жанры книг: {', '.join(preferences_data.get('book_genres', []))}\n"
                f"Любимые страны: {', '.join(preferences_data.get('countries', []))}\n"
                f"Десятилетия книг: {', '.join(preferences_data.get('book_decades', []))}\n"
                f"Любимые авторы: {', '.join(preferences_data.get('book_authors', []))}\n"
                f"Также недавно пользователь смотрел:\n"
                f"Жанры: {', '.join(preference.last_viewed_book_genres[-3:])}\n"
                f"Авторы: {', '.join(preference.last_viewed_authors[-3:])}\n\n"
                "Порекомендуй 10 книг.\n"
                "Просто напиши список книг в формате:\n"
                "1. Название книги — Автор\n"
                "Без комментариев и пояснений."
            )
            recommendations = ask_gigachat(prompt_books, access_token)
            preference.saved_book_recommendations = recommendations
            preference.book_recommendations_updated = timezone.now()
            preference.save()
        return redirect('recommendations_books')

    recommendations_list = []
    if preference.saved_book_recommendations:
        for line in preference.saved_book_recommendations.splitlines():
            if line.strip():
                recommendations_list.append({'text': line.strip()})
        recommendations_list = attach_books_to_recommendations(recommendations_list)
    return render(request, 'preferences/recommendations_books.html', {
        'recommendations': recommendations_list,
        'preference': preference,
    })