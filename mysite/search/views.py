from functools import lru_cache

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import ListView

from django.shortcuts import render, get_object_or_404
import requests

from .models import MovieCollections, CachedMovieQueries, CachedMovies

#headers = {"X-API-KEY": "D0RKYS2-28GM34H-MFSAZQF-VPMDCKK"}
headers = {"X-API-KEY": "5QT06C1-SQ44XCZ-QDBKQ9E-804RSH8"}


# Create your views here.
@login_required(login_url = 'login')
def browse_page(request):
    return render(request, 'search/browse.html', {"new_movies" : MovieCollections.objects.filter(topic_name='new')})

@login_required(login_url = 'login')
def film_page(request, kp_id):
    if MovieCollections.objects.filter(movie_data__id=kp_id):
        print("COLLECTIONS")
        return render(request, 'search/film_page.html', {'movie': MovieCollections.objects.get(movie_data__id=kp_id).movie_data})
    elif CachedMovies.objects.filter(movie_data__id=kp_id):
        print("CACHED")
        return render(request, 'search/film_page.html', {'movie': CachedMovies.objects.get(movie_data__id=kp_id).movie_data})
    print("NEW")
    movie = requests.get(url=f"https://api.kinopoisk.dev/v1.4/movie/{kp_id}", headers=headers).json()
    if CachedMovies.objects.count() >= 50:
        CachedMovies.objects.order_by("id").first().delete()
    CachedMovies.objects.create(movie_data=movie)
    return render(request, 'search/film_page.html', {'movie': movie})

@login_required(login_url = 'login')
def book_page(request, volumeId):
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes/{volumeId}").json()
    return render(request, 'search/book_page.html', {"book": response})


@login_required(login_url = 'login')
def search_page(request):
    return render(request, 'search/search_page.html')


@login_required(login_url = 'login')
def search_results(request):
    global data
    query = request.GET.get('search_query', '')
    item_type = request.GET.get('search_type', 'movie')
    years = request.GET.get('years', '')
    country = request.GET.get('country', '').split(",")
    genres = request.GET.getlist('genre', '!церемония')
    sort_by = request.GET.get("sort_by", "")

    if item_type == "movie":
        try:
            if years == "":
                data = get_object_or_404(CachedMovieQueries, query=query).movie_data
                print("CACHED QUERY 0")
            else:
                data = get_object_or_404(CachedMovieQueries, years=years, country=country, genres=genres).movie_data
                print("CACHED QUERY 1")
        except Http404:
            print("NEW QUERY")
            if years == "":
                result = requests.get(url=f"https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=5&query={query}",
                                      headers=headers)
            else:
                result = requests.get(
                    'https://api.kinopoisk.dev/v1.4/movie',
                    params={
                        "genres.name": genres,
                        "limit": 100,
                        "page": 1,
                        "notNullFields": ["poster.url", "description"],
                        "year": years,
                        "countries.name": country,
                    },
                    headers=headers)
            data = result.json()["docs"] if result.status_code == 200 else None

            if CachedMovieQueries.objects.count() >= 50:
                CachedMovieQueries.objects.order_by("id").first().delete()
            CachedMovieQueries.objects.create(query=query, years=years, country=country, genres=genres, movie_data=data)
            print("ADDED")

        match sort_by:
            case "year_lb":
                data = sorted(data, key=lambda x: x.get("year", 0), reverse=False)
            case "year_bl":
                data = sorted(data, key=lambda x: x.get("year", 0), reverse=True)
            case "rating_lb":
                data = sorted(data,
                              key=lambda x: (x.get("rating", {}).get("kp", 0), x.get("rating", {}).get("imdb", 0)),
                              reverse=False)
            case "rating_bl":
                data = sorted(data,
                              key=lambda x: (x.get("rating", {}).get("kp", 0), x.get("rating", {}).get("imdb", 0)),
                              reverse=True)
            case "votes_lb":
                data = sorted(data,
                              key=lambda x: (x.get("rating", {}).get("kp", 0), x.get("rating", {}).get("imdb", 0)),
                              reverse=False)
            case "votes_bl":
                data = sorted(data,
                              key=lambda x: (x.get("rating", {}).get("kp", 0), x.get("rating", {}).get("imdb", 0)),
                              reverse=True)
        return render(request, 'search/search_results.html', {"data": data})

    elif item_type == "book":
        result = requests.get(url=f"https://www.googleapis.com/books/v1/volumes?q={query}")
        b_data = result.json()["items"] if result.status_code == 200 else None
        return render(request, 'search/search_results.html', {"b_data": b_data})
