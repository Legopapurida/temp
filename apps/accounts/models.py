from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string

class OTPDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_devices')
    name = models.CharField(max_length=64, default='Email OTP')
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'email')
    
    def __str__(self):
        return f"{self.user.username} - {self.email}"

class OTPToken(models.Model):
    device = models.ForeignKey(OTPDevice, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def is_valid(self):
        if self.is_used:
            return False
        expiry_time = self.created_at + timedelta(minutes=5)
        return timezone.now() < expiry_time
    
    def mark_used(self):
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    @classmethod
    def generate_token(cls):
        return ''.join(random.choices(string.digits, k=6))