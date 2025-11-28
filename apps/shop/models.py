from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase


class ProductTag(TaggedItemBase):
    content_object = ParentalKey(
        'shop.ProductPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


@register_snippet
class ProductCategory(models.Model):
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
        verbose_name_plural = 'Product Categories'


@register_snippet
class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    panels = [
        FieldPanel('name'),
        FieldPanel('logo'),
    ]
    
    def __str__(self):
        return self.name


class ShopIndexPage(Page):
    """Shop listing page"""
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        products = self.get_children().live().order_by('-first_published_at')
        
        # Filter by category
        category = request.GET.get('category')
        if category:
            products = products.filter(productpage__categories__name__iexact=category)
        
        context['products'] = products
        context['categories'] = ProductCategory.objects.all()
        return context


class ProductPage(Page):
    """Individual product page"""
    
    # Basic info
    short_description = models.TextField(max_length=500)
    description = RichTextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Product details
    sku = models.CharField(max_length=50, unique=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True, help_text="L x W x H")
    
    # Media
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    # Categorization
    categories = ParentalManyToManyField('shop.ProductCategory', blank=True)
    brand = models.ForeignKey('shop.Brand', null=True, blank=True, on_delete=models.SET_NULL)
    tags = ClusterTaggableManager(through=ProductTag, blank=True)
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False, help_text="Digital product (no shipping)")
    
    content_panels = Page.content_panels + [
        FieldPanel('short_description'),
        FieldPanel('description'),
        MultiFieldPanel([
            FieldPanel('price'),
            FieldPanel('sale_price'),
        ], heading="Pricing"),
        MultiFieldPanel([
            FieldPanel('sku'),
            FieldPanel('stock_quantity'),
            FieldPanel('weight'),
            FieldPanel('dimensions'),
        ], heading="Product Details"),
        FieldPanel('featured_image'),
        FieldPanel('categories'),
        FieldPanel('brand'),
        FieldPanel('tags'),
        MultiFieldPanel([
            FieldPanel('is_featured'),
            FieldPanel('is_digital'),
        ], heading="Status"),
    ]
    
    parent_page_types = ['shop.ShopIndexPage']
    
    @property
    def current_price(self):
        """Return sale price if available, otherwise regular price"""
        return self.sale_price if self.sale_price else self.price
    
    @property
    def is_on_sale(self):
        """Check if product is on sale"""
        return self.sale_price is not None and self.sale_price < self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.is_on_sale:
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0