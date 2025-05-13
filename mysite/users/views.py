from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegisterForm
from .models import *
from search.movie_api_utils import *
from search.books_api_utils import *


def index(request):
    return render(request, 'users/index.html')


def ReDone(request):
    return render(request, 'users/register_done.html')


def AboutUs(request):
    return render(request, 'users/info_about_us.html')


def profile_view(request):
    return render(request, 'users/profile.html')


class RegisterUser(CreateView):
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('redone')


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'users/login-password.html'

    def get_success_url(self):
        redirect_to = self.request.POST.get("next", "/")
        return redirect_to


@login_required(login_url='login')
def add_review(request, item_type, id):
    if item_type == "movie":
        if request.method == "GET":
            movie = get_cached_movie(id)
            if not movie:
                movie = fetch_kinopoisk_movie(id)
                cache_movie(movie)

        if request.method == "POST":
            review_text = request.POST.get("review", "").strip()
            watch_date = request.POST.get("watch_date", "")
            Reviews.objects.update_or_create(
                user=request.user,
                item_type=item_type,
                item_id=str(id),
                defaults={'review': review_text, 'watch_date': watch_date} if watch_date else {'review': review_text}
            )

            return redirect('search:film_page', id)

        return render(request, 'users/add_review.html', {'movie': movie, 'item_type': 'movie'})
    
    if item_type == "book":
        if request.method == "GET":
            book = get_cached_book(id)
            if not book:
                book = fetch_single_book(id)
                cache_book(book)

        if request.method == "POST":
            review_text = request.POST.get("review", "").strip()
            watch_date = request.POST.get("watch_date", "")
            Reviews.objects.update_or_create(
                user=request.user,
                item_type=item_type,
                item_id=str(id),
                defaults={'review': review_text, 'watch_date': watch_date} if watch_date else {'review': review_text}
            )

            return redirect('search:book_page', id)

        return render(request, 'users/add_review.html', {'book': book, 'item_type': 'book'})


@login_required(login_url='login')
def diary(request):
    return render(request, 'users/diary.html')