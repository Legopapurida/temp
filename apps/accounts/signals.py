from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to handle user creation - OTP devices are created manually when user enables 2FA
    """
    if created:
        # User profile creation is handled in the community app
        pass