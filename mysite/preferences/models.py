from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Preference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_movie_genres = models.ManyToManyField('Genre', related_name='movie_users')
    favorite_book_genres = models.ManyToManyField('Genre', related_name='book_users')
    class Meta:
        verbose_name = "Preference"

class Genre(models.Model):
    name = models.CharField(max_length=50)


    class Meta:
        verbose_name = "Genre"


    def __str__(self):
        return self.name
    
    
