from django.db import models
from django.contrib.auth import get_user_model
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey

User = get_user_model()


class FormField(AbstractFormField):
    page = ParentalKey('ContactPage', on_delete=models.CASCADE, related_name='form_fields')


class ContactPage(AbstractEmailForm):
    """Contact form page"""
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)
    
    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro'),
        InlinePanel('form_fields', label='Form Fields'),
        FieldPanel('thank_you_text'),
    ]
    
    def process_form_submission(self, form):
        submission = super().process_form_submission(form)
        
        # Create HelpTicket from form submission
        HelpTicket.objects.create(
            name=form.cleaned_data.get('name', ''),
            email=form.cleaned_data.get('email', ''),
            subject=form.cleaned_data.get('subject', 'Contact Form Submission'),
            message=form.cleaned_data.get('message', ''),
        )
        
        return submission


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


@register_snippet
class HelpTicket(models.Model):
    """Help tickets from contact form submissions"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    admin_notes = RichTextField(blank=True, help_text='Internal notes for staff')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('email'),
        FieldPanel('subject'),
        FieldPanel('message'),
        FieldPanel('status'),
        FieldPanel('priority'),
        FieldPanel('assigned_to'),
        FieldPanel('admin_notes'),
        FieldPanel('resolved_at'),
    ]
    
    def __str__(self):
        return f"{self.subject} - {self.name}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Help Ticket'
        verbose_name_plural = 'Help Tickets'