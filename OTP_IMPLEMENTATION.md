# Custom OTP Service Implementation

## Overview
Implemented a custom OTP (One-Time Password) service from scratch without using django-otp plugin, along with middleware fixes and custom allauth templates.

## Features Implemented

### 1. Custom OTP Models
- **OTPDevice**: Manages user's OTP devices (email-based)
- **OTPToken**: Stores generated tokens with expiry and usage tracking

### 2. OTP Service (`apps/accounts/services.py`)
- `create_device()`: Creates OTP device for user
- `generate_and_send_token()`: Generates 6-digit token and sends via email
- `verify_token()`: Verifies token and marks as used
- `user_has_device()`: Checks if user has active OTP device

### 3. Fixed Middleware (`apps/accounts/middleware.py`)
- Removed django-otp dependency
- Fixed redirect loops by properly handling account URLs
- Added skip paths for static/media files
- Uses custom OTP service for device checking

### 4. Updated Views
- **setup_2fa_view**: Enable 2FA using custom service
- **verify_otp_view**: Verify tokens using custom service
- **disable_2fa_view**: Disable 2FA and clear session
- **custom_logout_view**: Clear OTP session on logout

### 5. Custom Templates

#### Email Management (`templates/account/email/email.html`)
- Modern gradient design
- Better UX with icons and badges
- Improved button grouping
- Confirmation dialogs for destructive actions

#### Password Change (`templates/account/password/password_change_form.html`)
- Enhanced security features
- Password requirements display
- Show/hide password toggle
- Password strength indicator (JavaScript)
- Modern styling with gradients

### 6. Admin Interface
- Registered OTPDevice and OTPToken models
- Proper list displays and filters
- Readonly fields for timestamps
- Prevented manual token creation

### 7. Management Command
- `cleanup_otp_tokens`: Removes expired tokens
- Configurable retention period (default: 7 days)

### 8. Tests
- Comprehensive test coverage for OTP service
- View testing for 2FA functionality
- Token expiry and validation tests

## Security Features

### Token Security
- 6-digit numeric tokens
- 5-minute expiry time
- Single-use tokens (marked as used after verification)
- Automatic cleanup of old tokens

### Session Management
- OTP verification stored in session
- Session cleared on logout
- Middleware enforces verification for protected pages

### Email Security
- Tokens sent only to verified email addresses
- Clear email templates with expiry information
- Failed send attempts handled gracefully

## Configuration

### Settings Changes
- Removed django-otp from INSTALLED_APPS
- Removed OTPMiddleware from MIDDLEWARE
- Updated OTP email settings
- Custom token validity configuration

### URL Structure
```
/accounts/setup-2fa/     - Enable 2FA
/accounts/verify-otp/    - Verify OTP token
/accounts/disable-2fa/   - Disable 2FA
/accounts/logout/        - Custom logout (clears OTP session)
```

## Database Schema

### OTPDevice
- user (ForeignKey to User)
- name (CharField, default: 'Email OTP')
- email (EmailField)
- is_active (BooleanField)
- created_at (DateTimeField)

### OTPToken
- device (ForeignKey to OTPDevice)
- token (CharField, 6 digits)
- created_at (DateTimeField)
- used_at (DateTimeField, nullable)
- is_used (BooleanField)

## Usage

### Enable 2FA
1. User visits `/accounts/setup-2fa/`
2. System creates OTPDevice for user's email
3. User redirected to profile with success message

### Login with 2FA
1. User logs in normally
2. Middleware detects active OTP device
3. User redirected to `/accounts/verify-otp/`
4. Token sent to user's email
5. User enters token to complete login

### Disable 2FA
1. User visits `/accounts/disable-2fa/`
2. Confirmation required with security warnings
3. All OTP devices deactivated
4. Session cleared

## Maintenance

### Token Cleanup
Run periodically to clean expired tokens:
```bash
python manage.py cleanup_otp_tokens --days 7
```

### Monitoring
- Admin interface shows all devices and tokens
- Failed verification attempts logged
- Email send failures handled gracefully

## Benefits Over django-otp
- No external dependencies
- Full control over token generation and validation
- Simplified codebase
- Custom email templates
- Better integration with existing user model
- Easier to extend and modify