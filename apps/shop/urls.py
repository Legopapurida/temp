from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    
    # Checkout URLs
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.process_order, name='process_order'),
    path('calculate-shipping/', views.calculate_shipping, name='calculate_shipping'),
    
    # Order URLs
    path('order/<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Wishlist URLs
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Account URLs
    path('account/', views.account_dashboard, name='account_dashboard'),
    path('account/addresses/', views.manage_addresses, name='manage_addresses'),
    path('account/addresses/add/', views.add_address, name='add_address'),
    path('account/addresses/<int:address_id>/edit/', views.edit_address, name='edit_address'),
    path('account/addresses/<int:address_id>/delete/', views.delete_address, name='delete_address'),
    path('account/profile/', views.edit_profile, name='edit_profile'),
    path('account/loyalty/', views.loyalty_points, name='loyalty_points'),
    
    # Review URLs
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('product/<int:product_id>/reviews/', views.product_reviews, name='product_reviews'),
    
    # Search URLs
    path('search/', views.search_products, name='search_products'),
    
    # AJAX URLs
    path('wishlist/remove-ajax/', views.remove_from_wishlist_ajax, name='remove_from_wishlist_ajax'),
    path('cart/quick-add/', views.quick_add_to_cart, name='quick_add_to_cart'),
    
    # Currency switching
    path('set-currency/', views.set_currency, name='set_currency'),
]