from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from phonenumber_field.modelfields import PhoneNumberField
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet


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

        # Filter by brand
        brand = request.GET.get('brand')
        if brand:
            products = products.filter(productpage__brand__name__iexact=brand)

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

    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0


# ============================================================================
# USER MANAGEMENT & PROFILES
# ============================================================================

class UserProfile(models.Model):
    """Extended user profile for e-commerce"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop_profile')
    phone = PhoneNumberField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    # Preferences
    currency = models.CharField(max_length=3, default='USD')
    language = models.CharField(max_length=5, default='en')
    newsletter_subscribed = models.BooleanField(default=True)

    # Loyalty
    loyalty_points = models.PositiveIntegerField(default=0)
    loyalty_tier = models.CharField(
        max_length=20,
        choices=[
            ('bronze', 'Bronze'),
            ('silver', 'Silver'),
            ('gold', 'Gold'),
            ('platinum', 'Platinum'),
        ],
        default='bronze'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Address(models.Model):
    """User addresses for shipping and billing"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    type = models.CharField(
        max_length=10,
        choices=[
            ('shipping', 'Shipping'),
            ('billing', 'Billing'),
        ]
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company = models.CharField(max_length=100, blank=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = CountryField()
    phone = PhoneNumberField(blank=True)

    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}, {self.country}"


# ============================================================================
# PRODUCT VARIANTS & ATTRIBUTES
# ============================================================================

class ProductAttribute(models.Model):
    """Product attributes like color, size, material"""
    name = models.CharField(max_length=50)
    type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('number', 'Number'),
            ('color', 'Color'),
            ('image', 'Image'),
        ]
    )

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """Values for product attributes"""
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    color_code = models.CharField(max_length=7, blank=True)  # For color attributes
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariant(models.Model):
    """Product variants (size, color combinations)"""
    product = models.ForeignKey(ProductPage, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=50, unique=True)
    attributes = models.ManyToManyField(ProductAttributeValue)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        attrs = ', '.join([str(attr) for attr in self.attributes.all()])
        return f"{self.product.title} - {attrs}"

    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.price


# ============================================================================
# SHOPPING CART
# ============================================================================

class Cart(models.Model):
    """Shopping cart"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} - {self.user or 'Guest'}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_weight(self):
        return sum(item.total_weight for item in self.items.all())


class CartItem(models.Model):
    """Items in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductPage, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product', 'variant']

    @property
    def unit_price(self):
        return self.variant.current_price if self.variant else self.product.current_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    @property
    def total_weight(self):
        weight = self.variant.weight if self.variant else self.product.weight
        return (weight or 0) * self.quantity


# ============================================================================
# COUPONS & DISCOUNTS
# ============================================================================

@register_snippet
class Coupon(models.Model):
    """Discount coupons"""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    discount_type = models.CharField(
        max_length=20,
        choices=[
            ('percentage', 'Percentage'),
            ('fixed', 'Fixed Amount'),
            ('free_shipping', 'Free Shipping'),
            ('buy_x_get_y', 'Buy X Get Y'),
        ]
    )

    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Usage limits
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_limit_per_user = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    # Restrictions
    categories = models.ManyToManyField(ProductCategory, blank=True)
    products = models.ManyToManyField(ProductPage, blank=True)
    first_order_only = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    def is_valid(self, user=None, cart_total=0):
        """Check if coupon is valid"""
        now = timezone.now()

        if not self.is_active:
            return False, "Coupon is not active"

        if now < self.valid_from or now > self.valid_until:
            return False, "Coupon has expired"

        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "Coupon usage limit reached"

        if cart_total < self.minimum_amount:
            return False, f"Minimum order amount is ${self.minimum_amount}"

        if user and self.first_order_only:
            if Order.objects.filter(user=user).exists():
                return False, "Coupon is for first orders only"

        return True, "Valid"


# ============================================================================
# ORDERS & PAYMENTS
# ============================================================================

class Order(models.Model):
    """Customer orders"""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Status
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')

    # Addresses
    billing_address = models.JSONField()
    shipping_address = models.JSONField()

    # Coupon
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate unique order number"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductPage, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Snapshot of product data at time of order
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Payment(models.Model):
    """Payment records"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('bank_transfer', 'Bank Transfer'),
        ('cod', 'Cash on Delivery'),
        ('store_credit', 'Store Credit'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=100, unique=True)

    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    # Gateway data
    gateway = models.CharField(max_length=50)  # stripe, paypal, etc.
    gateway_transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount}"


# ============================================================================
# SHIPPING
# ============================================================================

@register_snippet
class ShippingMethod(models.Model):
    """Available shipping methods"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Pricing
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    cost_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Delivery time
    min_delivery_days = models.PositiveIntegerField()
    max_delivery_days = models.PositiveIntegerField()

    # Restrictions
    max_weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def calculate_cost(self, weight, subtotal):
        """Calculate shipping cost based on weight and order value"""
        if self.free_shipping_threshold and subtotal >= self.free_shipping_threshold:
            return 0

        return self.base_cost + (self.cost_per_kg * weight)


class Shipment(models.Model):
    """Order shipments"""
    SHIPMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=50, blank=True)

    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=SHIPMENT_STATUS_CHOICES, default='pending')

    shipped_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Shipment for Order {self.order.order_number}"


# ============================================================================
# LOYALTY & REWARDS
# ============================================================================

class LoyaltyTransaction(models.Model):
    """Loyalty points transactions"""
    TRANSACTION_TYPES = [
        ('earned', 'Points Earned'),
        ('redeemed', 'Points Redeemed'),
        ('expired', 'Points Expired'),
        ('bonus', 'Bonus Points'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loyalty_transactions')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField()
    description = models.CharField(max_length=255)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.points} points ({self.type})"


class Wishlist(models.Model):
    """User wishlists"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    name = models.CharField(max_length=100, default='My Wishlist')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s {self.name}"


class WishlistItem(models.Model):
    """Items in wishlist"""
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductPage, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['wishlist', 'product', 'variant']

    def __str__(self):
        return f"{self.product.title} in {self.wishlist.name}"


# ============================================================================
# REVIEWS & RATINGS
# ============================================================================

class ProductReview(models.Model):
    """Product reviews and ratings"""
    product = models.ForeignKey(ProductPage, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, null=True, blank=True)

    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    review = models.TextField()

    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.product.title} - {self.rating} stars by {self.user.username}"
