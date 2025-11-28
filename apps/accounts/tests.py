from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import OTPDevice, OTPToken
from .services import OTPService

class OTPServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_device(self):
        device = OTPService.create_device(self.user)
        self.assertEqual(device.user, self.user)
        self.assertEqual(device.email, self.user.email)
        self.assertTrue(device.is_active)
    
    def test_user_has_device(self):
        self.assertFalse(OTPService.user_has_device(self.user))
        OTPService.create_device(self.user)
        self.assertTrue(OTPService.user_has_device(self.user))
    
    def test_token_generation(self):
        device = OTPService.create_device(self.user)
        token = OTPService.generate_and_send_token(device)
        self.assertEqual(len(token.token), 6)
        self.assertTrue(token.token.isdigit())
        self.assertFalse(token.is_used)
    
    def test_token_verification(self):
        device = OTPService.create_device(self.user)
        token = OTPService.generate_and_send_token(device)
        
        # Valid token should verify
        self.assertTrue(OTPService.verify_token(device, token.token))
        
        # Token should be marked as used
        token.refresh_from_db()
        self.assertTrue(token.is_used)
        
        # Used token should not verify again
        self.assertFalse(OTPService.verify_token(device, token.token))
    
    def test_token_expiry(self):
        device = OTPService.create_device(self.user)
        token = OTPToken.objects.create(device=device, token='123456')
        
        # Fresh token should be valid
        self.assertTrue(token.is_valid())
        
        # Expired token should not be valid
        token.created_at = timezone.now() - timedelta(minutes=10)
        token.save()
        self.assertFalse(token.is_valid())

class TwoFactorAuthViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_setup_2fa(self):
        """Test 2FA setup process"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test setup 2FA page
        response = self.client.get(reverse('accounts:setup_2fa'))
        self.assertEqual(response.status_code, 200)
        
        # Test enabling 2FA
        response = self.client.post(reverse('accounts:setup_2fa'))
        self.assertEqual(response.status_code, 302)
        
        # Check if device was created
        device = OTPDevice.objects.filter(user=self.user).first()
        self.assertIsNotNone(device)
        self.assertEqual(device.email, self.user.email)

    def test_otp_verification_page(self):
        """Test OTP verification page"""
        # Create device first
        device = OTPService.create_device(self.user)
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('accounts:verify_otp'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'verification code')