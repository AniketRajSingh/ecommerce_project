# accounts/views.py
from django import forms
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from django.template.loader import render_to_string
from django.contrib.auth.models import User

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
        user = User.objects.create_user(username=username, password=password1)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        messages.success(request, 'Account created successfully!')
        return redirect('home')
    else:
        return render(request, 'account/login_signup_template.html')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            return redirect('home')  # Adjust the redirect URL as needed
    else:
        form = AuthenticationForm()
    return render(request, 'account/login_signup_template.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email', 'primary_phone_number', 'alternative_phone_number', 'first_name', 'last_name',
                  'permanent_street', 'permanent_city', 'permanent_state', 'permanent_pincode', 'permanent_landmark',
                  'shipping_street', 'shipping_city', 'shipping_state', 'shipping_pincode', 'shipping_landmark']

    email = forms.EmailField(label='Email Address')
    primary_phone_number = forms.CharField(label='Primary Phone Number', max_length=15)
    alternative_phone_number = forms.CharField(label='Alternative Phone Number', max_length=15)
    first_name = forms.CharField(label='First Name', max_length=30)
    last_name = forms.CharField(label='Last Name', max_length=30)

    # Permanent Address Fields
    permanent_street = forms.CharField(label='Street', max_length=255, required=False)
    permanent_city = forms.CharField(label='City', max_length=100, required=False)
    permanent_state = forms.CharField(label='State', max_length=100, required=False)
    permanent_pincode = forms.CharField(label='Pincode', max_length=20, required=False)
    permanent_landmark = forms.CharField(label='Landmark', max_length=255, required=False)

    # Shipping Address Fields
    shipping_street = forms.CharField(label='Street', max_length=255, required=False)
    shipping_city = forms.CharField(label='City', max_length=100, required=False)
    shipping_state = forms.CharField(label='State', max_length=100, required=False)
    shipping_pincode = forms.CharField(label='Pincode', max_length=20, required=False)
    shipping_landmark = forms.CharField(label='Landmark', max_length=255, required=False)

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
            return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'account/profile.html', {'form': form})


def login_signup_view(request):
    return render(request, 'login_signup_template.html')

def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Process the form data and send the password reset email
            form.save(request=request)
            messages.success(request, 'Password reset email sent.')
            return JsonResponse({'email_sent': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = PasswordResetForm()
    return render(request, 'account/password_reset.html', {'form': form})

def password_reset_confirm_view(request, uidb64, token):
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            # Process the form data and set the new password
            form.save()
            messages.success(request, 'Password reset successfully completed.')
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = SetPasswordForm()
    return JsonResponse({'html_content': render_to_string('account/password_reset.html', {'form': form})})

def password_reset_done_view(request):
    return render(request, 'account/password_reset.html')

def password_reset_complete_view(request):
    return render(request, 'account/password_reset.html')