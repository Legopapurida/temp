from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.utils import translation
from wagtail.models import Page
from .models import ErrorPage


class SearchView(TemplateView):
    template_name = 'search/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query', '')
        
        if query:
            context['results'] = Page.objects.live().search(query)
        else:
            context['results'] = Page.objects.none()
        
        context['query'] = query
        return context


def set_language(request):
    """Custom language setter that also updates user profile"""
    if request.method == 'POST':
        language = request.POST.get('language')
        next_url = request.POST.get('next', '/')
        
        if language:
            translation.activate(language)
            response = redirect(next_url)
            response.set_cookie('django_language', language)
            
            # Update user profile if authenticated
            if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
                request.user.userprofile.language = language
                request.user.userprofile.save(update_fields=['language'])
            
            return response
    
    return redirect('/')


def get_error_page(request, error_code):
    """Get custom error page from Wagtail or fallback to default"""
    try:
        error_page = ErrorPage.objects.live().get(error_code=str(error_code))
        return render(request, 'core/error_page.html', {
            'page': error_page,
            'error_code': error_code,
        }, status=error_code)
    except ErrorPage.DoesNotExist:
        return render(request, 'core/error_page.html', {
            'error_code': error_code,
            'error_title': f'Error {error_code}',
            'error_message': 'An error occurred. Please try again later.',
            'show_home_button': True,
            'show_back_button': True,
        }, status=error_code)


def handler401(request, exception=None):
    return get_error_page(request, 401)


def handler403(request, exception=None):
    return get_error_page(request, 403)


def handler404(request, exception=None):
    return get_error_page(request, 404)


def handler500(request):
    return get_error_page(request, 500)


def handler502(request):
    return get_error_page(request, 502)


def handler503(request):
    return get_error_page(request, 503)
