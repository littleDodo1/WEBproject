from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import PreferenceForm
from .models import Preference
from search.models import CachedBooks, CachedMovies
from django.contrib.auth.decorators import login_required
import re
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
from preferences.api_gigachat_utils import ask_gigachat, get_access_token


@login_required(login_url='login')
def profile_view(request):
    return render(request, 'users/profile.html')

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



def attach_movies_to_recommendations(recommendations):
    for rec in recommendations:
        text = rec.get("text", "")
        match = re.search(r"[«\"](.+?)[»\"]", text)
        if match:
            title = match.group(1)
        else:
            title = text.split("—")[0].split("(")[0].strip()
            title = " ".join(title.split()[:3])

        search_results = fetch_movie_search(title, years="", country="", genres="")
        if search_results:
            movie_data = search_results[0]
            kp_id = movie_data.get('id')
            cached = get_cached_movie(kp_id)
            if cached:
                rec["movie"] = cached
                rec["movie_id"] = cached.get('id')
            else:
                full_data = fetch_kinopoisk_movie(kp_id)
                if full_data:
                    cache_movie(full_data)
                    rec["movie"] = full_data
                    rec["movie_id"] = full_data.get('id')
                else:
                    rec["movie"] = None
                    rec["movie_id"] = None
        else:
            rec["movie"] = None
            rec["movie_id"] = None
    return recommendations
def attach_books_to_recommendations(recommendations):
    for rec in recommendations:
        text = rec.get("text", "")
        match = re.search(r'[«"*](.+?)[»"*]', text)
        if match:
            title = match.group(1)
        else:
            title = text.split("—")[0].split("(")[0].strip()
            title = " ".join(title.split()[:3])

        rec["book"] = None
        rec["book_key"] = None
        rec["covers"] = None

        search_results = fetch_books_search(title, genres="")
        if not search_results:
            continue

        api_book_data = search_results[0]
        key = api_book_data.get('key', '')

        book_data, summary, substance, covers = get_cached_book(key)

        if not book_data:
            book_data = api_book_data

            access_token = get_access_token()
            if access_token:
                promptA = (
                    "Ты — помощник по генерации краткого содержания книг.\n\n"
                    "Напиши 6 предложений о книге на русском языке.\n"
                    f"Название книги (переведи на русский, если нужно): {title}\n"
                    "Без комментариев и лишних слов."
                )  
                summary = ask_gigachat(promptA, access_token)
                promptB = (
                    "Ты — помощник по генерации содержания книг.\n\n"
                    "Напиши 10–15 предложений о книге на русском языке.\n"
                    f"Название книги (переведи на русский, если нужно): {title}\n"
                    "Без комментариев и лишних слов."
                )
                substance = ask_gigachat(promptB, access_token)
            else:
                summary = ""
                substance = ""

            cover_id = book_data.get("cover_i")
            cache_book(book_data, content=summary, substance=substance, covers=cover_id)

        rec["book"] = book_data
        if book_data and isinstance(book_data, dict):
            if not rec["covers"]:
                rec["covers"] = book_data.get("covers", [None])[0]
            key = book_data.get("key", "")
            if key.startswith("/works/"):
                rec["book_key"] = key.replace("/works/", "")
            else:
                rec["book_key"] = key
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
                "Порекомендуй 5 фильмов.\n"
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
                "You are a English book recommendation assistant.\n\n"
                "Based on user preferences:\n"
                f"Book genres: {', '.join(preferences_data.get('book_genres', []))}\n"
                f"Favorite countries: {', '.join(preferences_data.get('countries', []))}\n"
                f"Book decades: {', '.join(preferences_data.get('book_decades', []))}\n"
                f"Favorite authors: {', '.join(preferences_data.get('book_authors', []))}\n"
                f"Recently viewed:\n"
                f"Genres: {', '.join(preference.last_viewed_book_genres[-3:])}\n"
                f"Authors: {', '.join(preference.last_viewed_authors[-3:])}\n\n"
                "Recommend 5 books strictly in English.\n"
                "Provide only the list in the following format:\n"
                '1. "Book Title" — Author\n'
                "Do not add any comments or explanations."
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