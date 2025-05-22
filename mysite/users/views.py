from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegisterForm
from .models import *
from search.movie_api_utils import *
from search.books_api_utils import *
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings


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

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()

        token = user.generate_verify_token()

        subject = 'Подтвердите ваш email'
        confirm_url = f"{settings.SITE_URL}/verify-email/{token}/"
        message = (
            f"Здравствуйте, {user.username}!\n\n"
            f"Пожалуйста, подтвердите ваш email, перейдя по ссылке:\n"
            f"{confirm_url}\n\n"
            f"Спасибо за регистрацию!"
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return super().form_valid(form) 


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'users/login-password.html'

    def form_valid(self, form):
        user = form.get_user()

        if not user.email_verify:
            token = user.email_verify_token

            confirm_url = f"{settings.SITE_URL}/verify-email/{token}/"
            message = (
                f"Здравствуйте, {user.username}!\n\n"
                f"Для входа в аккаунт необходимо подтвердить ваш email.\n"
                f"Пожалуйста, перейдите по ссылке:\n{confirm_url}\n\n"
                f"Спасибо!"
            )

            send_mail(
                "Подтверждение email",
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return redirect('redone')

        return super().form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.POST.get("next", "/")
        return redirect_to


@login_required(login_url='login')
def add_review(request, item_type, id):
    if item_type == "movie":
        if request.method == "GET":
            movie = get_or_fetch_movie(id)

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
            book = get_or_fetch_book(id)

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


@login_required(login_url='login')
def history(request):
    raw_data = History.objects.filter(user=request.user)
    data = []

    for item in range(len(raw_data))[::-1]:

        if raw_data[item].item_type == "movie":
            movie = get_or_fetch_movie(int(raw_data[item].item_id))
            data.append({'type': 'movie','data': movie})

        elif raw_data[item].item_type == "book":
            book = get_or_fetch_book(raw_data[item].item_id)
            data.append({'type': 'book', 'data': book})

    return render(request, 'users/history.html', {'data': data})


@login_required(login_url='login')
def watchlist(request):
    raw_data = WishList.objects.filter(user=request.user)
    data = []

    for item in range(len(raw_data))[::-1]:

        if raw_data[item].item_type == "movie":
            movie = get_or_fetch_movie(int(raw_data[item].item_id))
            data.append({'type': 'movie', 'data': movie})

        elif raw_data[item].item_type == "book":
            book = get_or_fetch_book(raw_data[item].item_id)
            data.append({'type': 'book', 'data': book})

    return render(request, 'users/watchlist.html', {'data': data})
    

@login_required(login_url='login')
def rated_page(request):
    raw_data = Ratings.objects.filter(user=request.user)
    data = []

    for item in range(len(raw_data))[::-1]:

        if raw_data[item].item_type == "movie":
            movie = get_or_fetch_movie(int(raw_data[item].item_id))
            data.append({'type': 'movie', 'data': movie})

        elif raw_data[item].item_type == "book":
            book = get_or_fetch_book(raw_data[item].item_id)
            data.append({'type': 'book', 'data': book})

    return render(request, 'users/rated_page.html', {'data': data})


@login_required(login_url='login')
def RevAndRate(request):
    if request.method == "POST":
        Reviews.objects.filter(user=request.user, item_id=request.POST.get("item_id"), item_type=request.POST.get("item_type")).delete()

    data = []
    reviews = Reviews.objects.filter(user=request.user)

    for item in range(len(reviews))[::-1]:
        rating = Ratings.objects.filter(user=request.user, item_id=reviews[item].item_id)
        if reviews[item].item_type == 'movie':
            item_data = get_or_fetch_movie(int(reviews[item].item_id))
            item_type = 'movie'
        else:
            item_data = get_or_fetch_book(reviews[item].item_id)
            item_type = 'book'
        if len(rating) > 0:
            data.append({'type': item_type, 'data': item_data, 'review': reviews[item].review, 'rating': rating[0].grade, 'review_date': reviews[item].review_date, 'watch_date': reviews[item].watch_date})
        else:
            data.append({'type': item_type, 'data': item_data, 'review': reviews[item].review, 'review_date': reviews[item].review_date, 'watch_date': reviews[item].watch_date})

    return render(request, 'users/reviews.html', {'data': data})


@login_required(login_url='login')
def Profile(request):
    user = request.user
    context = {'username': user.username}

    return render(request, 'users/profile.html', context)


def custom_logout(request):
    logout(request)
    return redirect('index')


def verify_email(request, token):
    user = get_object_or_404(CustomUser, email_verify_token=token)
    
    user.email_verify = True
    user.email_verify_token = ""
    user.save()

    return render(request, 'users/email_verified.html')
