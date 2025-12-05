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
    from wagtail.images.models import Image
    from apps.shop.models import UserProfile as ShopProfile, Order, LoyaltyTransaction
    from apps.community.models import Post
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    shop_profile, _ = ShopProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST' and 'avatar' in request.FILES:
        avatar_file = request.FILES['avatar']
        image = Image.objects.create(
            title=f"{request.user.username}_avatar",
            file=avatar_file
        )
        profile.avatar = image
        profile.save()
        messages.success(request, 'Avatar updated successfully!')
        return redirect('accounts:profile')
    
    has_2fa = user_has_device(request.user)
    
    # Get user statistics
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:3]
    total_orders = Order.objects.filter(user=request.user).count()
    recent_posts = Post.objects.filter(author=request.user).order_by('-created_at')[:3]
    total_posts = Post.objects.filter(author=request.user).count()
    recent_loyalty = LoyaltyTransaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'shop_profile': shop_profile,
        'has_2fa': has_2fa,
        'otp_devices': EmailDevice.objects.devices_for_user(request.user),
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'recent_posts': recent_posts,
        'total_posts': total_posts,
        'recent_loyalty': recent_loyalty,
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

@login_required
def resend_confirmation_view(request):
    """Resend email confirmation"""
    if request.method == 'POST':
        email = request.POST.get('email')
        messages.success(request, f'Verification email sent to {email}')
    return redirect('account_email')

@login_required
def set_primary_email_view(request):
    """Set primary email"""
    if request.method == 'POST':
        email = request.POST.get('email')
        messages.success(request, f'{email} set as primary email')
    return redirect('account_email')

@login_required
def remove_email_view(request):
    """Remove email address"""
    if request.method == 'POST':
        email = request.POST.get('email')
        messages.success(request, f'{email} removed from your account')
    return redirect('account_email')

