from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

urlpatterns = [
    path('browse/', views.browse_page, name='browse'),
    path('film/<int:kp_id>/', views.film_page, name='film_page'),
    path('book/<slug:volumeId>/', views.book_page, name='book_page'),
    path('search/', views.search_page, name='search_page'),
    path('results/', views.search_results, name='results')
]
