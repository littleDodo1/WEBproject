from django.db import models
import json

# Create your models here.

class MovieCollections(models.Model):
    topic_name = models.CharField(max_length=20)
    movie_data = models.JSONField()
    def __str__(self):
        return f"{self.topic_name} - {json.dumps(self.movie_data)}"

class popularBooks(models.Model):
    book_data = models.JSONField()
    def __str__(self):
        return f"{json.dumps(self.book_data)}"

class CachedMovieQueries(models.Model):
    query = models.TextField()
    years = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    genres = models.TextField()
    movie_data = models.JSONField()
    def __str__(self):
        return f"{self.query}, {self.years}, {self.country}, {self.genres}, {json.dumps(self.movie_data)}"

class CachedMovies(models.Model):
    movie_data = models.JSONField()
    def __str__(self):
        return f"{json.dumps(self.movie_data)}"