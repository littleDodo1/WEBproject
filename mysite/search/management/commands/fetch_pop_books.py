from django.core.management.base import BaseCommand
import requests
from search.models import popularBooks

class Command(BaseCommand):
    help = 'Fetch movies from Google Books API and store them in the database'
#не юзать эту программу!
    def handle(self, *args, **kwargs):
        response = requests.get(
            url="https://api.kinopoisk.dev/v1.4/movie?page=1&limit=50&notNullFields=name&notNullFields=poster.url"
                "&type=movie&isSeries=false&status=&year=2025&votes.kp=1000-6666666&votes.imdb=1000-6666666",
            headers={"X-API-KEY": "D0RKYS2-28GM34H-MFSAZQF-VPMDCKK"},
        )
        data = response.json()["docs"]

        for film in data:
            newMovies.objects.create(movie_data=film)

        self.stdout.write(self.style.SUCCESS(f"Загружено {len(data)} фильмов."))
