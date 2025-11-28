from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet


@register_snippet
class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('artist', 'Artist'),
        ('manager', 'Manager'),
        ('qa', 'QA Tester'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True)
    avatar = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('role'),
        FieldPanel('bio'),
        FieldPanel('avatar'),
        MultiFieldPanel([
            FieldPanel('linkedin_url'),
            FieldPanel('twitter_url'),
            FieldPanel('github_url'),
        ], heading="Social Links"),
        FieldPanel('is_featured'),
        FieldPanel('order'),
    ]
    
    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"


class TeamMemberBlock(blocks.StructBlock):
    member = blocks.PageChooserBlock(target_model='teams.TeamMember', required=False)
    name = blocks.CharBlock(max_length=100, required=False)
    role = blocks.CharBlock(max_length=50, required=False)
    bio = blocks.TextBlock(required=False)
    avatar = ImageChooserBlock(required=False)
    
    class Meta:
        template = 'blocks/team_member.html'
        icon = 'user'


class TeamsIndexPage(Page):
    """Teams and developers listing page"""
    
    intro = models.TextField(blank=True)
    
    # Team sections
    team_content = StreamField([
        ('team_member', TeamMemberBlock()),
        ('rich_text', blocks.RichTextBlock()),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('team_content'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        context['featured_members'] = TeamMember.objects.filter(is_featured=True)
        context['all_members'] = TeamMember.objects.all()
        return context
    
    class Meta:
        verbose_name = "Teams Index Page"