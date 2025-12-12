from django.conf import settings


def user_preferences(request):
    """Add user currency and language preferences to template context"""
    currency = 'USD'
    language = 'en'
    
    if request.user.is_authenticated:
        try:
            profile = request.user.shop_profile
            currency = profile.currency or 'USD'
            language = profile.language or 'en'
        except:
            pass
    
    # Fallback to session
    currency = request.session.get('user_currency', currency)
    
    return {
        'user_currency': currency,
        'user_language': language,
        'available_currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD'],
        'available_languages': settings.LANGUAGES,
    }
