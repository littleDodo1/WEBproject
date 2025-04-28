from django.contrib import admin
from .models import MovieCollections, popularBooks, CachedMovieQueries, CachedMovies
# Register your models here.
admin.site.register(MovieCollections)
admin.site.register(popularBooks)
admin.site.register(CachedMovieQueries)
admin.site.register(CachedMovies)