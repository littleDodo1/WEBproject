from django.core.management.base import BaseCommand
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Update popular genres and authors based on view history'

    def handle(self, *args, **options):
        CustomUser.update_popular_choices()
        self.stdout.write(self.style.SUCCESS('Successfully updated popular choices'))