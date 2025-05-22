from .models import CachedMovies, MovieCollections, CachedMovieQueries
import requests
import os
from dotenv import load_dotenv

load_dotenv()

headers = {"X-API-KEY": os.getenv('API_KEY')}


def get_cached_movie(kp_id):
    movie_entry = CachedMovies.objects.filter(movie_data__id=kp_id).first()
    if not movie_entry:
        movie_entry = MovieCollections.objects.filter(movie_data__id=kp_id).first()
    return movie_entry.movie_data if movie_entry else None


def fetch_kinopoisk_movie(kp_id):
    response = requests.get(f"https://api.kinopoisk.dev/v1.4/movie/{kp_id}", headers=headers)
    return response.json() if response.status_code == 200 else None


def cache_movie(movie):
    if CachedMovies.objects.count() >= 75:
        CachedMovies.objects.order_by("id").first().delete()
    CachedMovies.objects.update_or_create(movie_data=movie)

def get_or_fetch_movie(kp_id):
    movie = get_cached_movie(int(kp_id))
    if not movie:
        movie = fetch_kinopoisk_movie(kp_id)
        cache_movie(movie)
    return movie


def cache_query(query, years, country, genres, movie_data):
    if CachedMovieQueries.objects.count() >= 50:
        CachedMovieQueries.objects.order_by("id").first().delete()
    CachedMovieQueries.objects.update_or_create(query=query, years=years, country=country, genres=genres, movie_data=movie_data)


def fetch_movie_search(query, years, country, genres):
    if years == "":
        url = f"https://api.kinopoisk.dev/v1.4/movie/search"
        params = {"page": 1, "limit": 18, "query": query}
    else:
        url = "https://api.kinopoisk.dev/v1.4/movie"
        params = {
            "genres.name": genres,
            "limit": 120,
            "page": 1,
            "notNullFields": ["poster.url", "description"],
            "year": years,
            "countries.name": country,
        }

    response = requests.get(url, headers=headers, params=params)
    return response.json().get("docs") if response.status_code == 200 else []


def sort_movies(data, sort_by):
    if not data:
        return []

    match sort_by:
        case "year_lb":
            return sorted(data, key=lambda x: x.get("year", 0))
        case "year_bl":
            return sorted(data, key=lambda x: x.get("year", 0), reverse=True)
        case "rating_lb":
            return sorted(data, key=lambda x: (x.get("rating", {}).get("kp", 0), x.get("rating", {}).get("imdb", 0)))
        case "rating_bl":
            return sorted(data, key=lambda x: (x.get("rating", {}).get("kp", 0), x.get("rating", {}).get("imdb", 0)),
                          reverse=True)
        case "votes_lb":
            return sorted(data, key=lambda x: x.get("votes", {}).get("kp", 0))
        case "votes_bl":
            return sorted(data, key=lambda x: x.get("votes", {}).get("kp", 0), reverse=True)
        case _:
            return data
