from django.core.management.base import BaseCommand
import requests
from search.models import MovieCollections
import os
from dotenv import load_dotenv

load_dotenv()

class Command(BaseCommand):
    help = 'Fetch movies from Kinopoisk API and store them in the database'

    def handle(self, *args, **kwargs):
        MovieCollections.objects.filter(topic_name="new").delete()
        response = requests.get(
            url="https://api.kinopoisk.dev/v1.4/movie?page=1&limit=50&notNullFields=name&notNullFields=poster.url"
                "&notNullFields=description&type=movie&isSeries=false&status=&year=2025&votes.kp=1000-6666666&votes"
                ".imdb=1000-6666666",
            headers = {"X-API-KEY": os.getenv('API_KEY')},
        )
        data = response.json()["docs"]

        for movie in data:
            MovieCollections.objects.create(topic_name="new", movie_data=movie)

        self.stdout.write(self.style.SUCCESS(f"Загружено {len(data)} фильмов."))
