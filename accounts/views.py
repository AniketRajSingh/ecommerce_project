# accounts/views.py
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile, Address
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.forms.models import modelformset_factory



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
