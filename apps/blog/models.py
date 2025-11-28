from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase


class BlogTag(TaggedItemBase):
    content_object = ParentalKey(
        'blog.BlogPost',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code")
    
    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('color'),
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Blog Categories'


class BlogIndexPage(Page):
    """Blog listing page"""
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        posts = self.get_children().live().order_by('-first_published_at')
        
        # Filter by category if specified
        category = request.GET.get('category')
        if category:
            posts = posts.filter(blogpost__categories__name__iexact=category)
        
        context['posts'] = posts
        context['categories'] = BlogCategory.objects.all()
        return context


class BlogPost(Page):
    """Individual blog post"""
    
    # Content
    excerpt = models.TextField(max_length=500, help_text="Brief description for listings")
    body = RichTextField()
    
    # Meta
    date = models.DateTimeField("Post date", auto_now_add=True)
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_posts'
    )
    
    # Featured image
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    # Categorization
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)
    tags = ClusterTaggableManager(through=BlogTag, blank=True)
    
    # SEO
    is_featured = models.BooleanField(default=False, help_text="Show in featured posts")
    
    content_panels = Page.content_panels + [
        FieldPanel('excerpt'),
        FieldPanel('body'),
        FieldPanel('author'),
        FieldPanel('featured_image'),
        FieldPanel('categories'),
        FieldPanel('tags'),
        FieldPanel('is_featured'),
    ]
    
    parent_page_types = ['blog.BlogIndexPage']
    
    def get_context(self, request):
        context = super().get_context(request)
        # Related posts
        context['related_posts'] = BlogPost.objects.live().exclude(id=self.id).filter(
            categories__in=self.categories.all()
        ).distinct()[:3]
        return context