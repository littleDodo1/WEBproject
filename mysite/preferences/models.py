from django.db import models
from users.models import CustomUser

class MovieGenre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class BookGenre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Decade(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class BookAuthor(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class MovieDirector(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Preference(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    favorite_movie_genres = models.ManyToManyField(MovieGenre, related_name='movie_users')
    favorite_book_genres = models.ManyToManyField(BookGenre, related_name='book_users')
    favorite_countries = models.ManyToManyField(Country, related_name='country_users')
    favorite_movie_decades = models.ManyToManyField(Decade, related_name='movie_decade_users')
    favorite_book_decades = models.ManyToManyField(Decade, related_name='book_decade_users')
    favorite_book_authors = models.ManyToManyField(BookAuthor, related_name='book_authors_users')
    favorite_movie_directors = models.ManyToManyField(MovieDirector, related_name='movie_directors_users')
    saved_movie_recommendations = models.TextField(blank=True, null=True)
    saved_book_recommendations = models.TextField(blank=True, null=True)
    book_recommendations_updated = models.DateTimeField(blank=True, null=True)
    movie_recommendations_updated = models.DateTimeField(blank=True, null=True)
    last_viewed_movie_genres = models.JSONField(default=list, blank=True)
    last_viewed_book_genres = models.JSONField(default=list, blank=True)
    last_viewed_countries = models.JSONField(default=list, blank=True)
    last_viewed_authors = models.JSONField(default=list, blank=True)
    last_viewed_directors = models.JSONField(default=list, blank=True)

    def add_last_viewed_movie_genres(self, genres):
        self._update_last_viewed('last_viewed_movie_genres', genres)

    def add_last_viewed_book_genres(self, genres):
        self._update_last_viewed('last_viewed_book_genres', genres)

    def add_last_viewed_countries(self, countries):
        self._update_last_viewed('last_viewed_countries', countries)

    def add_last_viewed_authors(self, authors):
        self._update_last_viewed('last_viewed_authors', authors)

    def add_last_viewed_directors(self, directors):
        self._update_last_viewed('last_viewed_directors', directors)

    def _update_last_viewed(self, field_name, new_items):
        current_items = getattr(self, field_name, []).copy()
        
        for item in reversed(new_items):
            if item in current_items:
                current_items.remove(item)
            current_items.insert(0, item)
        
        setattr(self, field_name, current_items[:5])
        self.save()
