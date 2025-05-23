from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from users.models import *
from preferences.views import ask_gigachat, get_access_token
from .models import *
from preferences.models import Preference

from .movie_api_utils import (
    fetch_kinopoisk_movie,
    get_cached_movie,
    cache_movie,
    cache_query,
    fetch_movie_search,
    sort_movies,
    get_or_fetch_movie
)
from .books_api_utils import (
    fetch_books_search,
    cache_book_query,
    sort_books,
    get_cached_book,
    fetch_single_book,
    cache_book,
    get_or_fetch_book
)


@login_required(login_url='login')
def browse_page(request):
    popular_data = []
    popular = History.objects.annotate(count=Count('item_id')).order_by('count')[:20]
    for item in popular:
        if item.item_type == 'movie':
            movie = get_or_fetch_movie(item.item_id)
            if movie:
                popular_data.append({'type': 'movie', 'data': movie})
        else:
            book = get_or_fetch_book(item.item_id)
            if book:
                popular_data.append({'type': 'book', 'data': book})
    return render(request, 'search/browse.html', {
        "new_movies": MovieCollections.objects.filter(topic_name='new'),
        "popular_items": popular_data
    })


@login_required(login_url='login')
def film_page(request, kp_id):
    movie = get_cached_movie(kp_id)
    if not movie:
        movie = fetch_kinopoisk_movie(kp_id)
        if movie:
            cache_movie(movie)
    genres = [genre['name'] for genre in movie.get('genres', [])] if movie else []
    countries = [country['name'] for country in movie.get('countries', [])] if movie else []
    directors = [person['name'] for person in movie.get('persons', []) if person.get('enProfession') == 'director'] if movie else []
    try:
        preference = Preference.objects.get(user=request.user)
        preference.add_last_viewed_movie_genres(genres)
        preference.add_last_viewed_countries(countries)
        preference.add_last_viewed_directors(directors)
    except Preference.DoesNotExist:
        pass

    genres = [genre['name'] for genre in movie.get('genres', [])] if movie else []
    countries = [country['name'] for country in movie.get('countries', [])] if movie else []
    directors = [person['name'] for person in movie.get('persons', []) if
                 person.get('enProfession') == 'director'] if movie else []
    try:
        preference = Preference.objects.get(user=request.user)
        preference.add_last_viewed_movie_genres(genres)
        preference.add_last_viewed_countries(countries)
        preference.add_last_viewed_directors(directors)
    except Preference.DoesNotExist:
        pass

    if request.method == "POST":
        rating_value = request.POST.get("rating")
        is_wished = request.POST.get("isWished")

        if rating_value:
            Ratings.objects.update_or_create(
                user=request.user,
                item_type="movie",
                item_id=str(kp_id),
                defaults={'grade': rating_value}
            )
        if is_wished is not None:
            wished_obj, created = WishList.objects.get_or_create(
                user=request.user,
                item_type="movie",
                item_id=kp_id
            )
            if not created:
                wished_obj.delete()
                return JsonResponse({'status': 'removed'})
            return JsonResponse({'status': 'added'})

    rating_qs = Ratings.objects.filter(item_type='movie', item_id=kp_id)
    avg_rating = round(rating_qs.aggregate(avg=Avg('grade'))['avg'] or 0, 2)
    user_rating_obj = rating_qs.filter(user=request.user).first()
    user_rating = user_rating_obj.grade if user_rating_obj else None
    is_reviewed = Reviews.objects.filter(item_type='movie', item_id=kp_id, user=request.user).exists()
    is_wished = WishList.objects.filter(user=request.user, item_type='movie', item_id=kp_id).exists()
    data = []

    reviews = Reviews.objects.filter(item_type='movie', item_id=kp_id)

    for item in range(len(reviews))[::-1]:
        elem = reviews[item]
        nickname = CustomUser.objects.filter(id=elem.user_id)[0].username
        review = elem.review
        exists = Ratings.objects.filter(user=elem.user, item_id=kp_id).exists()
        grade = Ratings.objects.filter(user=elem.user, item_id=kp_id)[0].grade if exists else None

        data.append({'nick':nickname, 'review': review, 'grade': grade})

    History.objects.filter(user=request.user, item_type="movie", item_id=kp_id).delete()
    History.objects.create(user=request.user, item_type="movie", item_id=kp_id)
    if History.objects.filter(user=request.user).count() > 60:
        History.objects.filter(user=request.user).order_by("id").first().delete()

    return render(request, 'search/film_page.html', {
        'movie': movie,
        'genres': genres,
        'countries': countries,
        'directors': directors,
        'rating': avg_rating,
        'user_rating': user_rating,
        'is_reviewed': is_reviewed,
        'is_wished': is_wished,
        'data': data,
    })



@login_required(login_url='login')
def book_page(request, key):
    book, summary, substance, cover_id = get_cached_book(key)
    if not book:
        book = fetch_single_book(key)
        title = book['title'] if isinstance(book, dict) else book.title
        if book:
            access_token = get_access_token()
            if access_token:
                promptA = (
                    "Ты - помощник по генерации краткого содержания книг.\n\n"
                    "Напиши без каких либо комментариев, благодарения, вопросов от тебя 6 предложений о книге.\n"
                    "Мне нужно только описание без лишних слов, также учитывай что в названиях могут быть литературные слова\n"
                    f"Название книги: {title}"                    )
                summary = ask_gigachat(promptA, access_token)
                promptB = (
                    "Ты - помощник по генерации содержания книг.\n\n"
                    "Напиши без каких либо комментариев, благодарения, вопросов от тебя 10-15 предложений о книге.\n"
                    f"Название книги: {title}"                      )
                substance = ask_gigachat(promptB, access_token)   
            else:
                summary = ""
                substance = ""  
            cover_id = book.get("cover_i")
            cache_book(book, content=summary, substance=substance, covers=[cover_id] if cover_id else [])
        
    genres = book.get("subjects", [])[:5] if book else []
    authors = book.get("author_name", []) if book else []

    try:
        preference = Preference.objects.get(user=request.user)
        preference.add_last_viewed_book_genres(genres)
        preference.add_last_viewed_authors(authors)
    except Preference.DoesNotExist:
        pass

    if request.method == "POST":
        rating_value = request.POST.get("rating")
        is_wished = request.POST.get("isWished")

        if rating_value:
            Ratings.objects.update_or_create(
                user=request.user,
                item_type="book",
                item_id=str(key),
                defaults={'grade': rating_value}
            )
        if is_wished is not None:
            wished_obj, created = WishList.objects.get_or_create(
                user=request.user,
                item_type="book",
                item_id=key
            )
            if not created:
                wished_obj.delete()
                return JsonResponse({'status': 'removed'})
            return JsonResponse({'status': 'added'})

    rating_qs = Ratings.objects.filter(item_type='book', item_id=key)
    avg_rating = round(rating_qs.aggregate(avg=Avg('grade'))['avg'] or 0, 2)
    user_rating_obj = rating_qs.filter(user=request.user).first()
    user_rating = user_rating_obj.grade if user_rating_obj else None
    is_reviewed = Reviews.objects.filter(item_type='book', item_id=key, user=request.user).exists()

    is_wished = WishList.objects.filter(user=request.user, item_type='book', item_id=key).exists()

    if History.objects.count() >= 100:
        History.objects.order_by("id").first().delete()
    History.objects.update_or_create(user=request.user, item_type="book", item_id=key)
    data = []

    reviews = Reviews.objects.filter(item_type='book', item_id=key)

    for item in range(len(reviews))[::-1]:
        elem = reviews[item]
        nickname = CustomUser.objects.filter(id=elem.user_id)[0].username
        review = elem.review
        exists = Ratings.objects.filter(user=elem.user, item_id=key).exists()
        grade = Ratings.objects.filter(user=elem.user, item_id=key)[0].grade if exists else None

        data.append({'nick': nickname, 'review': review, 'grade': grade})

    History.objects.filter(user=request.user, item_type="book", item_id=key).delete()
    History.objects.create(user=request.user, item_type="book", item_id=key)
    if History.objects.filter(user=request.user).count() > 60:
        History.objects.filter(user=request.user).order_by("id").first().delete()
    return render(request, 'search/book_page.html', {
        'book': book,
        'genres': genres,
        'authors': authors,
        'rating': avg_rating,
        'user_rating': user_rating,
        'is_reviewed': is_reviewed,
        'is_wished': is_wished,
        'data': data,
        'summary': summary,
        'substance': substance,
        'cover_id': cover_id
    })

@login_required
def book_substance_view(request, book_key):
    book_data, content, substance = get_cached_book(f"/works/{book_key}")

    context = {
        'title': book_data.get('title', 'Без названия'),
        'substance': substance,
        'book_key': book_key
    }

    return render(request, 'search/book_substance.html', context)

@login_required
def book_substance_view(request, book_key):
    book_data, content, substance, _ = get_cached_book(f"/works/{book_key}")
    
    context = {
        'title': book_data.get('title', 'Без названия'),
        'substance': substance,
        'book_key': book_key
    }
    
    return render(request, 'search/book_substance.html', context)


@login_required(login_url='login')
def search_page(request):
    return render(request, 'search/search_page.html')


@login_required(login_url='login')
def search_results(request):
    query = request.GET.get('search_query', '')
    item_type = request.GET.get('search_type', '')
    years = request.GET.get('years', '')
    country = request.GET.get('country', '').split(",")
    genres = request.GET.getlist('genre') or ['!церемония']
    sort_by = request.GET.get("sort_by", "")
    param_type = request.GET.get("type", "")

    if item_type == "movie":
        try:
            if not param_type:
                data = get_object_or_404(CachedMovieQueries, query=query).movie_data
                print(data)
            else:
                data = get_object_or_404(CachedMovieQueries, years=years, country=country, genres=genres).movie_data
        except Http404:
            data = fetch_movie_search(query, years, country, genres)
            cache_query(query, years, country, genres, data)

        data = sort_movies(data, sort_by)
        return render(request, 'search/search_results.html', {"data": data})

    elif item_type == "book":
        try:
            if not param_type:
                data = get_object_or_404(CachedBookQueries, query=query).book_data
            else:
                data = get_object_or_404(CachedBookQueries, genres=genres[0] if genres else "").book_data
        except Http404:
            data = fetch_books_search(query, genres[0])
            cache_book_query(query, genres[0], data)

        data = sort_books(data, sort_by)
        return render(request, 'search/search_results.html', {"b_data": data, "type": param_type})