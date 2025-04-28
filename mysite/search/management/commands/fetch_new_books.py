from django.core.management.base import BaseCommand
import requests
from search.models import BookCollections

class Command(BaseCommand):
    help = 'Fetch books from Google Books API and store them in the database'
#не юзать эту программу!
    def handle(self, *args, **kwargs):
        url = "https://www.googleapis.com/books/v1/volumes"

        params = {
            "q": "*",
            "printType": "books",
            "orderBy": "newest",
            "langRestrict": "ru",
        }
        data = requests.get(url, params=params).json()["items"]

        for book in data:
            BookCollections.objects.create(topic_name="new", book_data=book)

        self.stdout.write(self.style.SUCCESS(f"Загружено {len(data)} книг."))