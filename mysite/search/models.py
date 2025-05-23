from django.db import models


# Create your models here.

class MovieCollections(models.Model):
    topic_name = models.CharField(max_length=20)
    movie_data = models.JSONField()


class BookCollections(models.Model):
    topic_name = models.CharField(max_length=20)
    book_data = models.JSONField()


class CachedMovieQueries(models.Model):
    query = models.TextField()
    years = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    genres = models.TextField()
    movie_data = models.JSONField()


class CachedMovies(models.Model):
    movie_data = models.JSONField()


class CachedBookQueries(models.Model):
    query = models.TextField()
    genres = models.TextField()
    book_data = models.JSONField()


class CachedBooks(models.Model):
    book_data = models.JSONField()
    content = models.TextField(blank=True, null=True)
    substance = models.TextField(blank=True, null=True)
    covers = models.JSONField() 
