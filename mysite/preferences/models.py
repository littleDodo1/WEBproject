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
    favorite_book_authors = models.ManyToManyField(BookAuthor, blank=True)
    favorite_movie_directors = models.ManyToManyField(MovieDirector, blank=True)
    saved_movie_recommendations = models.TextField(blank=True, null=True)
    saved_book_recommendations = models.TextField(blank=True, null=True)
    book_recommendations_updated = models.DateTimeField(blank=True, null=True)
    movie_recommendations_updated = models.DateTimeField(blank=True, null=True)