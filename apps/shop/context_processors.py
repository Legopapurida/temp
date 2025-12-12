def user_preferences(request):
    """Add user's preferred currency and language to context"""
    currency = request.session.get('currency', 'USD')
    language = 'en'
    
    if request.user.is_authenticated:
        try:
            profile = request.user.shop_profile
            currency = profile.currency
            language = profile.language
        except:
            pass
    
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'CAD': 'CA$',
        'AUD': 'A$',
    }
    
    return {
        'user_currency': currency,
        'currency_symbol': currency_symbols.get(currency, '$'),
        'user_language': language,
        'available_currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD'],
    }
