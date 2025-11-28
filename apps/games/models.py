from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase


class GameTag(TaggedItemBase):
    content_object = ParentalKey(
        'games.GamePage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


@register_snippet
class GameCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class")
    
    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('icon'),
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Game Categories'


class GamesIndexPage(Page):
    """Games listing page"""
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        games = self.get_children().live().order_by('-first_published_at')
        
        # Filter by category
        category = request.GET.get('category')
        if category:
            games = games.filter(gamepage__categories__name__iexact=category)
        
        context['games'] = games
        context['categories'] = GameCategory.objects.all()
        return context


class GamePage(Page):
    """Individual game page"""
    
    # Basic info
    short_description = models.TextField(max_length=500)
    description = RichTextField()
    
    # Media
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    trailer_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    
    # Game details
    release_date = models.DateField(null=True, blank=True)
    platforms = models.CharField(max_length=200, blank=True, help_text="PC, Mobile, Console, etc.")
    age_rating = models.CharField(max_length=10, blank=True, help_text="E, T, M, etc.")
    
    # Links
    demo_link = models.URLField(blank=True, help_text="Free trial/demo link")
    download_link = models.URLField(blank=True)
    
    # Categorization
    categories = ParentalManyToManyField('games.GameCategory', blank=True)
    tags = ClusterTaggableManager(through=GameTag, blank=True)
    
    # Gallery
    gallery = StreamField([
        ('image', ImageChooserBlock()),
        ('video_embed', blocks.URLBlock(help_text="YouTube/Vimeo URL")),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('short_description'),
        FieldPanel('description'),
        FieldPanel('featured_image'),
        FieldPanel('trailer_url'),
        MultiFieldPanel([
            FieldPanel('release_date'),
            FieldPanel('platforms'),
            FieldPanel('age_rating'),
        ], heading="Game Details"),
        MultiFieldPanel([
            FieldPanel('demo_link'),
            FieldPanel('download_link'),
        ], heading="Links"),
        FieldPanel('categories'),
        FieldPanel('tags'),
        FieldPanel('gallery'),
    ]
    
    parent_page_types = ['games.GamesIndexPage']