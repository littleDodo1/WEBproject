from django.urls import path

from . import views
app_name = 'search'

urlpatterns = [
    path('browse/', views.browse_page, name='browse'),
    path('film/<int:kp_id>/', views.film_page, name='film_page'),
    path('book/<slug:key>/', views.book_page, name='book_page'),
    path('search/', views.search_page, name='search_page'),
    path('results/', views.search_results, name='results'),
    path('book/<str:book_key>/substance/', views.book_substance_view, name='book_substance'),
]