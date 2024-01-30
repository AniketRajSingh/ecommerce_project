from django.urls import path, include
from .views import login_signup_view, signup, user_login, user_logout, edit_profile
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('', include('allauth.urls')),
    path('', include('allauth.socialaccount.urls')),
    path('edit/', edit_profile, name='edit_profile'),
    path('login_signup/', login_signup_view, name='login_signup'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset.html'), name='password_reset_complete'),

]
