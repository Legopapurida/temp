from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from apps.community.models import UserProfile
from .forms import ProfileForm

@login_required
def profile_view(request):
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})

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