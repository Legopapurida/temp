from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.snippets.models import register_snippet
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


@register_snippet
class FAQCategory(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('order'),
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'FAQ Categories'
        ordering = ['order', 'name']


@register_snippet
class FAQ(models.Model):
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = RichTextField()
    order = models.IntegerField(default=0)
    
    panels = [
        FieldPanel('category'),
        FieldPanel('question'),
        FieldPanel('answer'),
        FieldPanel('order'),
    ]
    
    def __str__(self):
        return self.question
    
    class Meta:
        ordering = ['order', 'question']


class FAQPage(Page):
    """FAQ page"""
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        categories = FAQCategory.objects.prefetch_related('faqs').all()
        context['faq_categories'] = categories
        return context