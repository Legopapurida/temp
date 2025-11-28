from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import OTPDevice, OTPToken

class OTPService:
    @staticmethod
    def create_device(user, email=None):
        """Create OTP device for user"""
        email = email or user.email
        device, created = OTPDevice.objects.get_or_create(
            user=user,
            email=email,
            defaults={'name': 'Email OTP'}
        )
        return device
    
    @staticmethod
    def generate_and_send_token(device):
        """Generate and send OTP token"""
        # Invalidate old tokens
        OTPToken.objects.filter(device=device, is_used=False).update(is_used=True)
        
        # Generate new token
        token_value = OTPToken.generate_token()
        token = OTPToken.objects.create(device=device, token=token_value)
        
        # Send email
        subject = 'Brickaria - Your verification code'
        message = f'Your Brickaria verification code is: {token_value}\n\nThis code will expire in 5 minutes.'
        
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'OTP_EMAIL_SENDER', 'noreply@brickaria.com'),
            recipient_list=[device.email],
            fail_silently=False,
        )
        
        return token
    
    @staticmethod
    def verify_token(device, token_value):
        """Verify OTP token"""
        try:
            token = OTPToken.objects.get(
                device=device,
                token=token_value,
                is_used=False
            )
            if token.is_valid():
                token.mark_used()
                return True
        except OTPToken.DoesNotExist:
            pass
        return False
    
    @staticmethod
    def user_has_device(user):
        """Check if user has active OTP device"""
        return OTPDevice.objects.filter(user=user, is_active=True).exists()