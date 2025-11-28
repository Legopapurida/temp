from django.shortcuts import redirect
from django.urls import reverse
from .services import OTPService

class OTPRequiredMiddleware:
    """
    Middleware to enforce OTP verification for users with 2FA enabled
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Skip for admin, API, and static endpoints
        skip_paths = ['/admin/', '/api/', '/static/', '/media/', '/documents/']
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)
        
        # Skip for account-related URLs to prevent redirect loops
        if request.path.startswith('/accounts/'):
            return self.get_response(request)
        
        # Check if user has 2FA enabled but not verified in this session
        if OTPService.user_has_device(request.user):
            if not request.session.get('otp_verified', False):
                return redirect('accounts:verify_otp')
        
        return self.get_response(request)