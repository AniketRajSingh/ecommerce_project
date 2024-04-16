# accounts/views.py
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile, Address
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
import random
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt

def signup(request):
    if request.method == 'POST':
        print(request)
        username = request.POST.get('username')
        print(username)
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return JsonResponse({'success': False, 'error': 'Passwords do not match.'})

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'This username is already taken.'})

        user = User.objects.create_user(username=username, password=password1)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return JsonResponse({'success': True})
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

@csrf_protect
def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                otp = random.randint(100000, 999999)
                user.otp = otp
                user.save()
                send_otp_email(request, user, otp)
                return JsonResponse({'success': True, 'otp_sent': True})
            else:
                return JsonResponse({'success': False, 'error': 'User with this email does not exist.'})
        else:
            return JsonResponse({'success': False, 'error': form.errors})
    else:
        form = PasswordResetForm()
    return render(request, 'account/password_reset.html', {'form': form})

def send_otp_email(request, user, otp):
    subject = 'Password Reset OTP'
    message = f'Your OTP for password reset is: {otp}'
    from_email = 'your-email@example.com'
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)
    cache.set(f'otp_{user.email}', otp, settings.OTP_CACHE_TIMEOUT)

@csrf_protect
def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        print(otp)
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            cached_otp = cache.get(f'otp_{user.email}')
            if cached_otp and cached_otp == int(otp):
                return JsonResponse({'success': True, 'otp_verified': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid OTP.'})
        else:
            return JsonResponse({'success': False, 'error': 'User with this email does not exist.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@csrf_protect
def set_new_password(request):
    if request.method == 'POST':
        email = request.POST.get('email_newp')
        print(email)
        new_password = request.POST.get('new_password')
        user = User.objects.filter(email=email).first()

        if user:
            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True, 'password_changed': True})
        else:
            return JsonResponse({'success': False, 'error': 'User with this email does not exist.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'pincode', 'landmark']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email', 'primary_phone_number', 'alternative_phone_number', 'first_name', 'last_name']

    email = forms.EmailField(label='Email Address')
    primary_phone_number = forms.CharField(label='Primary Phone Number', max_length=15)
    alternative_phone_number = forms.CharField(label='Alternative Phone Number', max_length=15,required=False)
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

UserProfileFormSet = forms.inlineformset_factory(UserProfile, Address, form=AddressForm, extra=1)

@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_address = Address.objects.filter(user_profile=user_profile)
    
    user_form = UserProfileForm(instance=user_profile)
    address_forms = [AddressForm(instance=address) for address in user_address]

    if request.method == 'POST':
        if 'first_name' in request.POST:
            user_form = UserProfileForm(request.POST, instance=user_profile)
            if user_form.is_valid():
                user_form.save()
                return JsonResponse({'success': True}) 
            else:
                return JsonResponse({'success': False, 'user_errors': user_form.errors})
        elif 'email' in request.POST:
            email = request.POST.get('email')
            if User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                return JsonResponse({'success': False, 'error': 'This email address is already in use.'})
            else:
                return JsonResponse({'success': True})
        elif 'street' in request.POST:
            address_form = AddressForm(request.POST)
            if address_form.is_valid() and 'address_id' not in request.POST :
                address = address_form.save(commit=False)
                address.user_profile = user_profile
                address.save()
                return JsonResponse({'success': True, 'address_id': address.pk}) 
            elif address_form.is_valid() and 'address_id' in request.POST :
                return JsonResponse({'success': True}) 
            else:
                return JsonResponse({'success': False, 'address_errors': address_form.errors})

    return render(request, 'account/profile.html', {'user_form': user_form, 'address_forms': address_forms})

def delete_address(request, address_id):
    address = get_object_or_404(Address, pk=address_id)
    if request.method == 'DELETE':
        address.delete()
        return JsonResponse({'success': True}) 
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

def edit_address(request, address_id):
    address = get_object_or_404(Address, pk=address_id)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True}) 
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

def login_signup_view(request):
    return render(request, 'login_signup_template.html')

@csrf_exempt
def verify_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(request, username=request.user.username, password=password)
        if user is not None:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid password'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})