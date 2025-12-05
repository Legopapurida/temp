from django.urls import path
from django_otp.views import LoginView as OTPLoginView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('setup-2fa/', views.setup_2fa_view, name='setup_2fa'),
    path('disable-2fa/', views.disable_2fa_view, name='disable_2fa'),
    # Use django-otp built-in login view for OTP verification
    path('otp-login/', OTPLoginView.as_view(), name='otp_login'),
    # Email management views
    path('resend-confirmation/', views.resend_confirmation_view, name='account_resend_confirmation'),
    path('set-primary/', views.set_primary_email_view, name='account_set_primary'),
    path('remove-email/', views.remove_email_view, name='account_remove_email'),
]