from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from .models import GamePage, GameCategory
from taggit.models import Tag


class GamesByCategoryView(ListView):
    model = GamePage
    template_name = 'games/games_by_category.html'
    context_object_name = 'games'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(GameCategory, name__iexact=self.kwargs['category_slug'])
        return GamePage.objects.live().filter(categories=self.category).order_by('-first_published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class GamesByTagView(ListView):
    model = GamePage
    template_name = 'games/games_by_tag.html'
    context_object_name = 'games'
    paginate_by = 12
    
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
        return GamePage.objects.live().filter(tags=self.tag).order_by('-first_published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context