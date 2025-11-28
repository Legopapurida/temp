from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from modelcluster.fields import ParentalKey


class FormField(AbstractFormField):
    page = ParentalKey('ContactPage', on_delete=models.CASCADE, related_name='form_fields')


class ContactPage(AbstractEmailForm):
    """Contact form page"""
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)
    
    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro'),
        FieldPanel('thank_you_text'),
    ]


class FAQPage(Page):
    """FAQ page"""
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]