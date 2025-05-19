import requests
from .models import *
from users.models import Ratings, History

def get_cached_book(key):
    book_entry = (CachedBooks.objects.filter(book_data__key=key).first() or CachedBooks.objects.filter(book_data__key=f"/works/{key}").first())
    if not book_entry:
        book_entry = BookCollections.objects.filter(book_data__key=key).first()
    return (book_entry.book_data, book_entry.content) if book_entry else (None, None)


def cache_book(book, content=None):
    if CachedBooks.objects.count() >= 50:
        CachedBooks.objects.order_by("id").first().delete()
    CachedBooks.objects.create(book_data=book, content=content)


def cache_book_query(query, genres, book_data):
    if CachedBookQueries.objects.count() >= 50:
        CachedBookQueries.objects.order_by("id").first().delete()
    CachedBookQueries.objects.create(query=query, genres=genres, book_data=book_data)


def fetch_single_book(key):
    response = requests.get(f"https://openlibrary.org/works/{key}.json")
    return response.json() if response.status_code == 200 else None


def fetch_books_search(query, genres):
    if query:
        data = requests.get(url=f"https://openlibrary.org/search.json?q={query}")
        return data.json().get("docs") if data.status_code == 200 else None

    url = f"https://openlibrary.org/subjects/{genres}.json?limit=120"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json().get("works", [])

def sort_books(data, sort_by):
    if not data:
        return []

    keys = [x.get("key") for x in data]

    ratings_count = Ratings.objects.filter(item_type='book', item_id__in=keys).values('item_id').annotate(count=models.Count('id'))
    ratings_map = {entry['item_id']: entry['count'] for entry in ratings_count}

    votes_count = History.objects.filter(item_type='book', item_id__in=keys).values('item_id').annotate(count=models.Count('id'))
    votes_map = {entry['item_id']: entry['count'] for entry in votes_count}

    match sort_by:
        case "year_lb":
            return sorted(data, key=lambda x: x.get("created", 0))
        case "year_bl":
            return sorted(data, key=lambda x: x.get("created", 0), reverse=True)
        case "rating_lb":
            return sorted(data, key=lambda x: ratings_map.get(x.get("key", ""), 0))
        case "rating_bl":
            return sorted(data, key=lambda x: ratings_map.get(x.get("key", ""), 0), reverse=True)
        case "votes_lb":
            return sorted(data, key=lambda x: votes_map.get(x.get("key", ""), 0))
        case "votes_bl":
            return sorted(data, key=lambda x: votes_map.get(x.get("key", ""), 0), reverse=True)
        case _:
            return data