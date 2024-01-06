# accounts/views.py
from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django import forms
from accounts.models import UserProfile

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            return redirect('home')  # Adjust the redirect URL as needed
    else:
        form = UserCreationForm()
    return render(request, 'account/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            return redirect('home')  # Adjust the redirect URL as needed
    else:
        form = AuthenticationForm()
    return render(request, 'account/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email', 'address', 'phone_number', 'first_name', 'last_name']

    email = forms.EmailField(label='Email Address')
    address = forms.CharField(label='Address', widget=forms.Textarea(attrs={'rows': 3}), required=False)
    phone_number = forms.CharField(label='Phone Number', max_length=15)
    first_name = forms.CharField(label='First Name', max_length=30)
    last_name = forms.CharField(label='Last Name', max_length=30)

    def save(self, commit=True):
        # Save the UserProfile instance
        user_profile = super(UserProfileForm, self).save(commit=False)
        user_profile.name = f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}"
        if commit:
            user_profile.save()

        # Save the User instance
        user = self.instance.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

        return user_profile

@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('edit_profile') 
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'account/profile.html', {'form': form})