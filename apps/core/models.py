from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet


class HeroBlock(blocks.StructBlock):
    """Hero section with image, title, and CTA"""
    title = blocks.CharBlock(max_length=200)
    subtitle = blocks.TextBlock(required=False)
    image = ImageChooserBlock()
    cta_text = blocks.CharBlock(max_length=50, required=False)
    cta_link = blocks.URLBlock(required=False)
    
    class Meta:
        template = 'blocks/hero_block.html'
        icon = 'image'


class FeatureBlock(blocks.StructBlock):
    """Feature section with icon, title, and description"""
    icon = blocks.CharBlock(max_length=50, help_text="Bootstrap icon class")
    title = blocks.CharBlock(max_length=100)
    description = blocks.TextBlock()
    
    class Meta:
        template = 'blocks/feature_block.html'
        icon = 'pick'


class GameCardBlock(blocks.StructBlock):
    """Game showcase card"""
    title = blocks.CharBlock(max_length=100)
    description = blocks.TextBlock()
    image = ImageChooserBlock()
    game_link = blocks.URLBlock(required=False)
    tags = blocks.ListBlock(blocks.CharBlock(max_length=30))
    
    class Meta:
        template = 'blocks/game_card_block.html'
        icon = 'media'


class StatsBlock(blocks.StructBlock):
    """Statistics/metrics display"""
    stat_value = blocks.CharBlock(max_length=20)
    stat_label = blocks.CharBlock(max_length=50)
    icon = blocks.CharBlock(max_length=50, required=False)
    
    class Meta:
        template = 'blocks/stats_block.html'
        icon = 'order'


@register_snippet
class SocialMediaLink(models.Model):
    """Social media links for footer"""
    name = models.CharField(max_length=50)
    url = models.URLField()
    icon_class = models.CharField(max_length=50, help_text="Bootstrap icon class (e.g., bi-youtube)")
    order = models.PositiveIntegerField(default=0)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('url'),
        FieldPanel('icon_class'),
        FieldPanel('order'),
    ]
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class PrivacyPolicyPage(Page):
    """Privacy Policy page"""
    content = RichTextField()
    
    content_panels = Page.content_panels + [
        FieldPanel('content'),
    ]


class TermsOfServicePage(Page):
    """Terms of Service page"""
    content = RichTextField()
    
    content_panels = Page.content_panels + [
        FieldPanel('content'),
    ]


class AboutUsPage(Page):
    """About Us page"""
    description = RichTextField(blank=True, help_text="Main about us content")
    
    content_panels = Page.content_panels + [
        FieldPanel('description'),
    ]


class BasePage(Page):
    """Base page model with common fields"""
    
    class Meta:
        abstract = True