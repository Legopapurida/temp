from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ProductCategory, Brand, ProductPage, ProductAttribute, ProductAttributeValue,
    ProductVariant, UserProfile, Address, Cart, CartItem, Coupon, Order, OrderItem,
    Payment, ShippingMethod, Shipment, LoyaltyTransaction, Wishlist, WishlistItem,
    ProductReview
)

# Keep existing admin for Django admin
# Wagtail admin is handled in wagtail_hooks.py


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon']
    search_fields = ['name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'logo']
    search_fields = ['name']


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']
    list_filter = ['type']


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value', 'color_code']
    list_filter = ['attribute']
    search_fields = ['value']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['sku', 'price', 'sale_price', 'stock_quantity', 'is_active']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'price', 'stock_quantity', 'is_active']
    list_filter = ['is_active', 'product']
    search_fields = ['sku', 'product__title']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'loyalty_tier', 'loyalty_points', 'created_at']
    list_filter = ['loyalty_tier', 'newsletter_subscribed']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'first_name', 'last_name', 'city', 'country', 'is_default']
    list_filter = ['type', 'country', 'is_default']
    search_fields = ['user__username', 'first_name', 'last_name', 'city']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['added_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'subtotal', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def total_items(self, obj):
        return obj.total_items
    
    def subtotal(self, obj):
        return f"${obj.subtotal:.2f}"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'discount_type', 'discount_value', 'used_count', 'is_active', 'valid_until']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code', 'name']
    readonly_fields = ['used_count', 'created_at']
    filter_horizontal = ['categories', 'products']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'unit_price', 'total_price']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['payment_id', 'created_at', 'processed_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline, PaymentInline]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing order
            return self.readonly_fields + ['user', 'subtotal', 'tax_amount', 'shipping_cost', 'total_amount']
        return self.readonly_fields


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'order', 'method', 'status', 'amount', 'created_at']
    list_filter = ['method', 'status', 'gateway', 'created_at']
    search_fields = ['payment_id', 'order__order_number', 'gateway_transaction_id']
    readonly_fields = ['payment_id', 'created_at', 'processed_at']


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_cost', 'min_delivery_days', 'max_delivery_days', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['order', 'tracking_number', 'carrier', 'status', 'shipped_at']
    list_filter = ['status', 'carrier', 'shipped_at']
    search_fields = ['order__order_number', 'tracking_number']


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'points', 'description', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at']


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    readonly_fields = ['added_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['user__username', 'name']
    readonly_fields = ['created_at']
    inlines = [WishlistItemInline]


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_verified_purchase', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'is_approved', 'created_at']
    search_fields = ['product__title', 'user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'user')