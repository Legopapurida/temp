from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse
from apps.community.models import UserProfile
from .forms import ProfileForm, OTPVerificationForm
from .services import OTPService
from .models import OTPDevice

@login_required
def profile_view(request):
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    has_2fa = OTPService.user_has_device(request.user)
    return render(request, 'accounts/profile.html', {
        'profile': profile, 
        'has_2fa': has_2fa,
        'otp_devices': OTPDevice.objects.filter(user=request.user, is_active=True)
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

def setup_2fa_view(request):
    """Setup 2FA for user"""
    if not request.user.is_authenticated:
        return redirect('account_login')
    
    # Check if user already has 2FA enabled
    if OTPService.user_has_device(request.user):
        messages.info(request, '2FA is already enabled for your account.')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        # Create OTP device for user
        device = OTPService.create_device(request.user)
        messages.success(request, '2FA has been enabled for your account.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/setup_2fa.html')

def verify_otp_view(request):
    """Verify OTP token"""
    if not request.user.is_authenticated:
        return redirect('account_login')
    
    # Check if already verified in this session
    if request.session.get('otp_verified', False):
        return redirect('/')
    
    device = OTPDevice.objects.filter(user=request.user, is_active=True).first()
    if not device:
        messages.error(request, 'No 2FA device found. Please set up 2FA first.')
        return redirect('accounts:setup_2fa')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            if OTPService.verify_token(device, token):
                request.session['otp_verified'] = True
                messages.success(request, 'Successfully verified!')
                return redirect('/')
            else:
                messages.error(request, 'Invalid or expired token.')
    else:
        form = OTPVerificationForm()
        try:
            OTPService.generate_and_send_token(device)
            messages.info(request, 'A verification code has been sent to your email.')
        except Exception as e:
            messages.error(request, 'Failed to send verification code. Please try again.')
    
    return render(request, 'accounts/verify_otp.html', {'form': form})

@login_required
def disable_2fa_view(request):
    """Disable 2FA for user"""
    if request.method == 'POST':
        # Deactivate all OTP devices
        OTPDevice.objects.filter(user=request.user).update(is_active=False)
        # Clear OTP session
        request.session.pop('otp_verified', None)
        messages.success(request, '2FA has been disabled for your account.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/disable_2fa.html')

def custom_logout_view(request):
    """Custom logout view to clear OTP session"""
    # Clear OTP verification from session
    request.session.pop('otp_verified', None)
    # Redirect to allauth logout
    return redirect('account_logout')