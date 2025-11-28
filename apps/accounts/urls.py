from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('setup-2fa/', views.setup_2fa_view, name='setup_2fa'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('disable-2fa/', views.disable_2fa_view, name='disable_2fa'),
    path('logout/', views.custom_logout_view, name='logout'),
]