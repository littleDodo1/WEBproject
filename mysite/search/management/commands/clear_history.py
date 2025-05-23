from django.core.management.base import BaseCommand
from users.models import History


class Command(BaseCommand):
    help = 'Fetch movies from Kinopoisk API and store them in the database'

    def handle(self, *args, **kwargs):
        History.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"История очищена"))
