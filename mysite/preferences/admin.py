from django.contrib import admin
from .models import Preference, MovieGenre, BookGenre, Country, Decade, MovieDirector, BookAuthor
# Register your models here.


@admin.register(BookGenre)
class BookGenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(MovieGenre)
class MovieGenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(MovieDirector)
class MovieDirectorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Decade)
class DecadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    search_fields = ('user__username',)
    ordering = ('user',)
    filter_horizontal = (
        'favorite_countries',
        'favorite_book_genres',
        'favorite_movie_genres',
        'favorite_book_authors',
        'favorite_movie_directors',
        'favorite_book_decades',
        'favorite_movie_decades'
    )