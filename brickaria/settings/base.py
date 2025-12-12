import os
import warnings
from pathlib import Path

from decouple import config

# Suppress wagtailmenus warnings (third-party package issue)
warnings.filterwarnings('ignore', message='.*content_panels will have no effect on snippets editing.*')
warnings.filterwarnings('ignore', message='.*settings_panels will have no effect on snippets editing.*')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
PROJECT_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_DIR.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

WAGTAIL_APPS = [
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
    'wagtail.locales',

    'wagtail.contrib.settings',
    'wagtail.contrib.table_block',
    'modelcluster',
    'taggit',
]

THIRD_PARTY_APPS = [
    'wagtailseo',
    'wagtailmenus',
    'wagtail_localize',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_extensions',
    'crispy_forms',
    'crispy_bootstrap5',
    'axes',
    'django_otp',
    'django_otp.plugins.otp_email',
    'django_otp.plugins.otp_totp',
    'django_countries',
    'phonenumber_field',
    'djmoney',
]

LOCAL_APPS = [
    'apps.core',
    'apps.home',
    'apps.games',
    'apps.blog',
    'apps.shop',
    'apps.community',
    'apps.events',
    'apps.accounts',
    'apps.support',
    'apps.teams',
]

INSTALLED_APPS = DJANGO_APPS + WAGTAIL_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'apps.core.middleware.UserLanguageMiddleware',
    'apps.shop.middleware.UserPreferencesMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'brickaria.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtailmenus.context_processors.wagtailmenus',
                'apps.core.context_processors.footer_context',
                'apps.shop.context_processors.user_preferences',
            ],
        },
    },
]

WSGI_APPLICATION = 'brickaria.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='brickaria'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
from django.utils.translation import gettext_lazy as _

LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
    ('fr', _('French')),
    ('de', _('German')),
    ('it', _('Italian')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES
WAGTAIL_I18N_ENABLED = True
WAGTAILADMIN_PERMITTED_LANGUAGES = LANGUAGES

# Static files (CSS, JavaScript, Images)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Wagtail settings
WAGTAIL_SITE_NAME = "Brickaria"
WAGTAILADMIN_BASE_URL = 'http://localhost:8000'

# Base URL to use when referring to full URLs within the Wagtail admin backend
BASE_URL = 'http://localhost:8000'

# Search
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site ID
SITE_ID = 1

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Authentication
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth settings
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True

# Axes settings
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1

# Email settings (configure for production)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django OTP settings
OTP_EMAIL_SENDER = config('OTP_EMAIL_SENDER', default='noreply@brickaria.com')
OTP_EMAIL_SUBJECT = 'Brickaria - Your verification code'
OTP_EMAIL_BODY_TEMPLATE = 'Your Brickaria verification code is: {token}\n\nThis code will expire in 5 minutes.'
OTP_EMAIL_TOKEN_VALIDITY = 300  # 5 minutes in seconds

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Wagtail SEO
SEO_JS_ENABLED = True

# E-commerce Settings
# Payment Gateway Settings
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID', default='')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET', default='')

# Currency Settings
CURRENCIES = ('USD', 'EUR', 'GBP', 'CAD')
DEFAULT_CURRENCY = 'USD'

# Session Settings
SESSION_COOKIE_AGE = 86400 * 30  # 30 days
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Cart Settings
CART_SESSION_ID = 'cart'
CART_TIMEOUT = 86400 * 7  # 7 days

# Loyalty Settings
LOYALTY_POINTS_PER_DOLLAR = 1
LOYALTY_TIERS = {
    'bronze': {'min_points': 0, 'discount': 0},
    'silver': {'min_points': 1000, 'discount': 5},
    'gold': {'min_points': 5000, 'discount': 10},
    'platinum': {'min_points': 10000, 'discount': 15},
}

# Tax Settings
DEFAULT_TAX_RATE = 0.08  # 8%

# Shipping Settings
FREE_SHIPPING_THRESHOLD = 50.00
DEFAULT_SHIPPING_COST = 10.00

# Phone Number Settings
PHONENUMBER_DEFAULT_REGION = 'US'

# Countries Settings
COUNTRIES_FIRST = ['US', 'CA', 'GB', 'AU']

# Redis/Celery (for background tasks)
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
