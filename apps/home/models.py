from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet


class HeroSlideBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=200)
    subtitle = blocks.TextBlock(required=False)
    image = ImageChooserBlock()
    cta_text = blocks.CharBlock(max_length=50, required=False)
    cta_link = blocks.URLBlock(required=False)
    
    class Meta:
        template = 'blocks/hero_slide.html'
        icon = 'image'


class FeaturedGameBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    description = blocks.TextBlock()
    image = ImageChooserBlock()
    game_link = blocks.URLBlock(required=False)
    release_date = blocks.DateBlock(required=False)
    
    class Meta:
        template = 'blocks/featured_game.html'
        icon = 'media'


class AchievementBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    description = blocks.TextBlock()
    icon = blocks.CharBlock(max_length=50, help_text="Bootstrap icon class")
    
    class Meta:
        template = 'blocks/achievement.html'
        icon = 'success'


class VisionBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    description = blocks.RichTextBlock()
    image = ImageChooserBlock(required=False)
    
    class Meta:
        template = 'blocks/vision.html'
        icon = 'view'


class MetricBlock(blocks.StructBlock):
    value = blocks.CharBlock(max_length=20)
    label = blocks.CharBlock(max_length=50)
    icon = blocks.CharBlock(max_length=50, required=False)
    
    class Meta:
        template = 'blocks/metric.html'
        icon = 'order'


class ComingSoonGameBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    description = blocks.TextBlock()
    image = ImageChooserBlock()
    release_date = blocks.DateBlock(required=False)
    
    class Meta:
        template = 'blocks/coming_soon_game.html'
        icon = 'time'


@register_snippet
class AppStoreLink(models.Model):
    STORE_CHOICES = [
        ('playstore', 'Google Play Store'),
        ('appstore', 'Apple App Store'),
        ('steam', 'Steam'),
    ]
    
    name = models.CharField(max_length=50)
    store_type = models.CharField(max_length=20, choices=STORE_CHOICES)
    url = models.URLField()
    icon_class = models.CharField(max_length=50, help_text="CSS icon class")
    is_active = models.BooleanField(default=True)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('store_type'),
        FieldPanel('url'),
        FieldPanel('icon_class'),
        FieldPanel('is_active'),
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "App Store Link"
        verbose_name_plural = "App Store Links"


class HomePage(Page):
    """Modern landing page with comprehensive sections"""
    
    # Hero Slider
    hero_slides = StreamField([
        ('slide', HeroSlideBlock()),
    ], blank=True, use_json_field=True)
    
    # Featured Games
    featured_games = StreamField([
        ('game', FeaturedGameBlock()),
    ], blank=True, use_json_field=True)
    
    # Company Achievements
    achievements = StreamField([
        ('achievement', AchievementBlock()),
    ], blank=True, use_json_field=True)
    
    # Vision & Roadmap
    vision_content = StreamField([
        ('vision', VisionBlock()),
    ], blank=True, use_json_field=True)
    
    # Community Metrics
    community_metrics = StreamField([
        ('metric', MetricBlock()),
    ], blank=True, use_json_field=True)
    
    # Coming Soon Games
    coming_soon_games = StreamField([
        ('game', ComingSoonGameBlock()),
    ], blank=True, use_json_field=True)
    
    # Newsletter
    newsletter_title = models.CharField(max_length=100, default="Stay Updated")
    newsletter_description = models.TextField(blank=True)
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('hero_slides'),
        ], heading="Hero Slider"),
        
        MultiFieldPanel([
            FieldPanel('featured_games'),
        ], heading="Featured Games"),
        
        MultiFieldPanel([
            FieldPanel('achievements'),
        ], heading="Company Achievements"),
        
        MultiFieldPanel([
            FieldPanel('vision_content'),
        ], heading="Vision & Roadmap"),
        
        MultiFieldPanel([
            FieldPanel('community_metrics'),
        ], heading="Community Metrics"),
        
        MultiFieldPanel([
            FieldPanel('coming_soon_games'),
        ], heading="Coming Soon Games"),
        
        MultiFieldPanel([
            FieldPanel('newsletter_title'),
            FieldPanel('newsletter_description'),
        ], heading="Newsletter Section"),
    ]
    
    max_count = 1
    
    def get_context(self, request):
        context = super().get_context(request)
        context['app_store_links'] = AppStoreLink.objects.filter(is_active=True)
        return context
    
    class Meta:
        verbose_name = "Home Page"