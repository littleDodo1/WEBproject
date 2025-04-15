from django.db import models


# Create your models here.

class MovieCollections(models.Model):
    topic_name = models.CharField(max_length=20)
    movie_data = models.JSONField()


class popularBooks(models.Model):
    book_data = models.JSONField()

class CachedMovieQueries(models.Model):
    query = models.TextField()
    years = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    genres = models.TextField()
    movie_data = models.JSONField()

class CachedMovies(models.Model):
    movie_data = models.JSONField()