from django.urls import path, include
from .views import login_signup_view, signup, user_login, user_logout, edit_profile

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('', include('allauth.urls')),
    path('', include('allauth.socialaccount.urls')),
    path('edit/', edit_profile, name='edit_profile'),
    path('login_signup/', login_signup_view, name='login_signup')
]
