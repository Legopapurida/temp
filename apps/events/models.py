from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


class EventsIndexPage(Page):
    """Events listing page"""
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]


class EventPage(Page):
    """Individual event page"""
    description = RichTextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    is_online = models.BooleanField(default=False)
    registration_url = models.URLField(blank=True)
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('start_date'),
        FieldPanel('end_date'),
        FieldPanel('location'),
        FieldPanel('is_online'),
        FieldPanel('registration_url'),
        FieldPanel('max_attendees'),
        FieldPanel('featured_image'),
    ]
    
    parent_page_types = ['events.EventsIndexPage']