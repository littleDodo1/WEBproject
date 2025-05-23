import requests
from .models import *
from users.models import Ratings, History
from django.db.models import Avg


def get_cached_book(key):
    book_entry = (CachedBooks.objects.filter(book_data__key=key).first() or 
                 CachedBooks.objects.filter(book_data__key=f"/works/{key}").first())
    if book_entry:
        cover_id = book_entry.covers[0] if book_entry.covers and isinstance(book_entry.covers, list) else None
        return book_entry.book_data, book_entry.content, book_entry.substance, cover_id
    
    book_entry = BookCollections.objects.filter(book_data__key=key).first()
    if book_entry:
        return book_entry.book_data, book_entry.content, None, None
    
    return None, None, None, None


def cache_book(book, content=None, substance=None, covers=None):
    if CachedBooks.objects.count() >= 50:
        CachedBooks.objects.order_by("id").first().delete()
    CachedBooks.objects.create(book_data=book, content=content, substance=substance, covers=covers)


def cache_book_query(query, genres, book_data):
    if CachedBookQueries.objects.count() >= 50:
        CachedBookQueries.objects.order_by("id").first().delete()
    CachedBookQueries.objects.create(query=query, genres=genres, book_data=book_data)


def fetch_single_book(key):
    response = requests.get(f"https://openlibrary.org/works/{key}.json")
    return response.json() if response.status_code == 200 else None

def get_or_fetch_book(key):
    book = get_cached_book(key)
    if not book:
        book = fetch_single_book(key)
        cache_book(book)
    return book


def fetch_books_search(query, genres):
    if query:
        data = requests.get(url=f"https://openlibrary.org/search.json?q={query}")
        return data.json().get("docs") if data.status_code == 200 else None

    url = f"https://openlibrary.org/subjects/{genres}.json?limit=120"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json().get("works", [])


def RatingValue(book_data):
    book_id = book_data.get("key").split('/')[-1]
    ratings = Ratings.objects.filter(item_type='book', item_id=book_id).aggregate(Avg("grade")).get("grade__avg")
    return ratings if ratings else 0


def VotesValue(book_data):
    book_id = book_data.get("key").split('/')[-1]
    votes = History.objects.filter(item_type='book', item_id=book_id).count()
    return votes if votes else 0


def sort_books(data, sort_by):
    if not data:
        return []

    match sort_by:
        case "year_lb":
            return sorted(data, key=lambda x: x.get("first_publish_year", 0))
        case "year_bl":
            return sorted(data, key=lambda x: x.get("first_publish_year", 0), reverse=True)
        case "rating_lb":
            return sorted(data, key=lambda x: RatingValue(x))
        case "rating_bl":
            return sorted(data, key=lambda x: RatingValue(x), reverse=True)
        case "votes_lb":
            return sorted(data, key=lambda x: VotesValue(x))
        case "votes_bl":
            return sorted(data, key=lambda x: VotesValue(x), reverse=True)
        case _:
            return data
