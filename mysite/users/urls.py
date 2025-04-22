from django.urls import path
from . import views
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView,\
      PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('about/', views.AboutUs, name='about'),

    path('password-reset/',
        PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            email_template_name="users/password_reset_email.html",
            success_url=reverse_lazy("password_reset_done")
            ),
        name='password_reset'),

    path('password-reset/done/',
        PasswordResetDoneView.as_view(template_name="users/Password_reset_done.html"),
        name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete")
            ),

         name='password_reset_confirm'),
    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
         name='password_reset_complete'),
]
