from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse
from django_otp.decorators import otp_required
from django_otp.plugins.otp_email.models import EmailDevice
from django_otp import user_has_device
from apps.community.models import UserProfile
from .forms import ProfileForm

@login_required
def profile_view(request):
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    has_2fa = user_has_device(request.user)
    return render(request, 'accounts/profile.html', {
        'profile': profile, 
        'has_2fa': has_2fa,
        'otp_devices': EmailDevice.objects.devices_for_user(request.user)
    })

@login_required
def profile_edit_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            form.save_user(request.user)
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

@login_required
def setup_2fa_view(request):
    """Setup 2FA for user"""
    # Check if user already has 2FA enabled
    if user_has_device(request.user):
        messages.info(request, '2FA is already enabled for your account.')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        # Create email OTP device for user
        device = EmailDevice.objects.create(
            user=request.user,
            name='Email OTP',
            email=request.user.email
        )
        messages.success(request, '2FA has been enabled for your account.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/setup_2fa.html')



@login_required
def disable_2fa_view(request):
    """Disable 2FA for user"""
    if request.method == 'POST':
        # Delete all OTP devices
        EmailDevice.objects.devices_for_user(request.user).delete()
        messages.success(request, '2FA has been disabled for your account.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/disable_2fa.html')

