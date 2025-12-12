from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.utils import translation
from wagtail.models import Page


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
