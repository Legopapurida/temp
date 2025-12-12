from django.db import models
from django.contrib.auth.models import User
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


class CommunityIndexPage(Page):
    """Community hub page"""
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]


class UserProfile(models.Model):
    """Extended user profile for community features"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    discord_username = models.CharField(max_length=100, blank=True)
    twitch_username = models.CharField(max_length=100, blank=True)
    youtube_channel = models.URLField(blank=True)
    
    # Preferences
    currency = models.CharField(max_length=3, default='USD')
    language = models.CharField(max_length=5, default='en')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    newsletter_subscribed = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Post(models.Model):
    """Community posts - screenshots, videos, streams"""
    POST_TYPES = [
        ('screenshot', 'Screenshot'),
        ('video', 'Video'),
        ('stream', 'Stream'),
        ('text', 'Text Post'),
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='text')
    
    # Media
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    video_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title