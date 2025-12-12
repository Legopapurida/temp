from django.utils import translation


class UserLanguageMiddleware:
    """Middleware to set language from user profile"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
            user_language = request.user.userprofile.language
            if user_language:
                translation.activate(user_language)
                request.LANGUAGE_CODE = user_language
        
        response = self.get_response(request)
        return response
