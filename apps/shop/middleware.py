from django.utils import translation
from django.utils.deprecation import MiddlewareMixin


class UserPreferencesMiddleware(MiddlewareMixin):
    """Middleware to apply user's language and currency preferences"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                profile = request.user.shop_profile
                # Set language
                if profile.language:
                    translation.activate(profile.language)
                    request.LANGUAGE_CODE = profile.language
                
                # Set currency in session
                if profile.currency:
                    request.session['user_currency'] = profile.currency
            except:
                pass
        
        # Fallback to session or default
        if not hasattr(request, 'LANGUAGE_CODE'):
            language = request.session.get('django_language', 'en')
            translation.activate(language)
            request.LANGUAGE_CODE = language
