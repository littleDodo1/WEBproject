from django import forms
from .models import Genre, Preference

class PreferenceForm(forms.ModelForm):
    favorite_movie_genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Любимые жанры кино"
    )
    favorite_book_genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Любимые жанры книг"
    )

    class Meta:
        model = Preference
        fields = ['favorite_movie_genres', 'favorite_book_genres']
