from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django_otp.plugins.otp_email.models import EmailDevice

class Command(BaseCommand):
    help = 'Setup 2FA for users'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to enable 2FA for')
        parser.add_argument('--all', action='store_true', help='Enable 2FA for all users')

    def handle(self, *args, **options):
        if options['username']:
            try:
                user = User.objects.get(username=options['username'])
                self.setup_2fa_for_user(user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User {options["username"]} not found'))
        elif options['all']:
            users = User.objects.filter(is_active=True)
            for user in users:
                self.setup_2fa_for_user(user)
        else:
            self.stdout.write(self.style.ERROR('Please specify --username or --all'))

    def setup_2fa_for_user(self, user):
        if not user.email:
            self.stdout.write(self.style.WARNING(f'User {user.username} has no email address'))
            return
        
        device, created = EmailDevice.objects.get_or_create(
            user=user,
            email=user.email,
            defaults={'name': 'Email OTP', 'confirmed': True}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'2FA enabled for {user.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'2FA already enabled for {user.username}'))