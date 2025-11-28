from django.shortcuts import render
from django.views.generic import TemplateView
from wagtail.models import Page


class SearchView(TemplateView):
    template_name = 'search/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('query')
        
        if search_query:
            search_results = Page.objects.live().search(search_query)
            
            context.update({
                'search_query': search_query,
                'search_results': search_results,
            })
        
        return context