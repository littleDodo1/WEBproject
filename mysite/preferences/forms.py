from django import forms
from .models import Preference, MovieGenre, BookGenre, Country, Decade, BookAuthor, MovieDirector

class PreferenceForm(forms.ModelForm):
    favorite_movie_genres = forms.ModelMultipleChoiceField(
        queryset=MovieGenre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Любимые жанры фильмов"
    )
    favorite_book_genres = forms.ModelMultipleChoiceField(
        queryset=BookGenre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Любимые жанры книг"
    )
    favorite_countries = forms.ModelMultipleChoiceField(
        queryset=Country.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Любимые страны"
    )
    favorite_movie_decades = forms.ModelMultipleChoiceField(
        queryset=Decade.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Любимые десятилетия фильмов"
    )
    favorite_book_decades = forms.ModelMultipleChoiceField(
        queryset=Decade.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Любимые десятилетия книг"
    )
    favorite_book_authors = forms.ModelMultipleChoiceField(
        queryset=BookAuthor.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Любимые авторы книг"
    )
    favorite_movie_directors = forms.ModelMultipleChoiceField(
        queryset=MovieDirector.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Любимые режиссеры"
    )


    class Meta:
        model = Preference
        fields = [
            'favorite_movie_genres', 
            'favorite_book_genres', 
            'favorite_countries', 
            'favorite_movie_decades', 
            'favorite_book_decades',
            'favorite_book_authors',
            'favorite_movie_directors'
        ]