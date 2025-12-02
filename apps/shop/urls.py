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
    
    # Order URLs
    path('order/<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),
    
    # Wishlist URLs
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    
    # Account URLs
    path('account/', views.account_dashboard, name='account_dashboard'),
    path('account/addresses/', views.manage_addresses, name='manage_addresses'),
]