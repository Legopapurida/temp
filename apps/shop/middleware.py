from django.utils import translation
from django.utils.deprecation import MiddlewareMixin


class UserPreferencesMiddleware(MiddlewareMixin):
    """Middleware to apply user's language and currency preferences"""
    
    def process_request(self, request):
        LANGUAGE_SESSION_KEY = '_language'
        
        # Priority: session language > profile language
        language = request.session.get(LANGUAGE_SESSION_KEY)
        
        if not language and request.user.is_authenticated:
            try:
                profile = request.user.userprofile
                if hasattr(profile, 'language') and profile.language:
                    language = profile.language
                    request.session[LANGUAGE_SESSION_KEY] = language
                
                # Set currency in session
                if hasattr(profile, 'currency') and profile.currency:
                    request.session['user_currency'] = profile.currency
            except:
                pass
        
        if language:
            translation.activate(language)
            request.LANGUAGE_CODE = language
