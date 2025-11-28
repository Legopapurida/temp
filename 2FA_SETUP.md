# Two-Factor Authentication Setup

This document explains the 2FA implementation in Brickaria using email-based OTP verification.

## Features

- **Email-based OTP**: Users receive verification codes via email
- **Automatic enforcement**: Users with 2FA enabled must verify on each login
- **User-friendly templates**: Styled templates matching the website design
- **Admin management**: Admin interface to manage 2FA devices
- **Management commands**: CLI tools to enable/disable 2FA for users

## Installation

1. Install required package:
```bash
pip install django-otp
```

2. Run migrations:
```bash
python manage.py migrate
```

## Usage

### For Users

1. **Enable 2FA**: Go to Profile → Enable 2FA
2. **Login Process**: After login, enter the 6-digit code sent to your email
3. **Code Expiry**: Codes expire after 5 minutes

### For Administrators

1. **Enable 2FA for specific user**:
```bash
python manage.py setup_2fa --username <username>
```

2. **Enable 2FA for all users**:
```bash
python manage.py setup_2fa --all
```

3. **Manage devices**: Use Django admin at `/admin/otp_email/emaildevice/`

## Configuration

### Email Settings
Configure in `settings/base.py`:
```python
OTP_EMAIL_SENDER = 'noreply@brickaria.com'
OTP_EMAIL_SUBJECT = 'Brickaria - Your verification code'
OTP_EMAIL_BODY_TEMPLATE = 'Your Brickaria verification code is: {token}'
OTP_EMAIL_TOKEN_VALIDITY = 300  # 5 minutes
```

### Email Backend
For production, configure proper email backend:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Templates

The following templates have been created/updated:

- `templates/account/password/password_change_form.html` - Password change form
- `templates/account/email/email.html` - Email management
- `templates/accounts/setup_2fa.html` - 2FA setup page
- `templates/accounts/verify_otp.html` - OTP verification page
- `templates/accounts/profile.html` - Updated with 2FA status
- `templates/accounts/login.html` - Improved styling

## Security Features

- **Token expiry**: OTP codes expire after 5 minutes
- **Session verification**: Users must verify OTP for each session
- **Middleware protection**: Automatic redirection to OTP verification
- **Admin bypass**: Admin pages bypass OTP requirement

## Testing

Run tests:
```bash
python manage.py test apps.accounts
```

## Troubleshooting

1. **Email not received**: Check email backend configuration
2. **Invalid token**: Ensure code is entered within 5 minutes
3. **Middleware issues**: Check middleware order in settings
4. **Device not found**: User needs to enable 2FA first

## URLs

- `/accounts/setup-2fa/` - Setup 2FA
- `/accounts/verify-otp/` - Verify OTP code
- `/accounts/password/change/` - Change password
- `/accounts/email/` - Manage email addresses