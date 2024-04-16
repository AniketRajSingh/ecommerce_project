from django.urls import path, include
from .views import login_signup_view, signup, user_login, user_logout, edit_profile,edit_address,delete_address,password_reset_view, verify_otp,set_new_password, verify_password
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('', include('allauth.urls')),
    path('', include('allauth.socialaccount.urls')),
    path('edit/', edit_profile, name='edit_profile'),
    path('login_signup/', login_signup_view, name='login_signup'),
    path('reset_password/', password_reset_view, name='password_reset_view'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('set_new_password/', set_new_password, name='set_new_password'),
    path('edit_address/<int:address_id>/', edit_address, name='edit_address'),
    path('delete_address/<int:address_id>/', delete_address, name='delete_address'),
    path('verify-password/', verify_password, name='verify_password'),

]
