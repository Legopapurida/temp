from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.utils import timezone
from decimal import Decimal
import json
import stripe
from django.conf import settings

from .models import (
    ProductPage, ProductVariant, Cart, CartItem, Order, OrderItem,
    Payment, Coupon, UserProfile, Address, Wishlist, WishlistItem,
    ProductReview, ShippingMethod, LoyaltyTransaction
)


def get_or_create_cart(request):
    """Get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def cart_view(request):
    """Display shopping cart"""
    cart = get_or_create_cart(request)
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product', 'variant').all(),
    }
    return render(request, 'shop/cart.html', context)


@require_POST
def add_to_cart(request):
    """Add product to cart"""
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(ProductPage, id=product_id)
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id)
    
    cart = get_or_create_cart(request)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'message': f'{product.title} added to cart'
        })
    
    messages.success(request, f'{product.title} added to cart')
    return redirect('shop:cart')


@require_POST
def update_cart_item(request):
    """Update cart item quantity"""
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'cart_subtotal': float(cart.subtotal),
        })
    
    return redirect('shop:cart')


@require_POST
def remove_from_cart(request):
    """Remove item from cart"""
    item_id = request.POST.get('item_id')
    
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'cart_subtotal': float(cart.subtotal),
        })
    
    messages.success(request, 'Item removed from cart')
    return redirect('shop:cart')


@require_POST
def apply_coupon(request):
    """Apply coupon to cart"""
    coupon_code = request.POST.get('coupon_code', '').strip().upper()
    
    try:
        coupon = Coupon.objects.get(code=coupon_code)
        cart = get_or_create_cart(request)
        
        is_valid, message = coupon.is_valid(
            user=request.user if request.user.is_authenticated else None,
            cart_total=float(cart.subtotal)
        )
        
        if is_valid:
            request.session['applied_coupon'] = coupon.id
            messages.success(request, f'Coupon "{coupon_code}" applied successfully!')
        else:
            messages.error(request, message)
    
    except Coupon.DoesNotExist:
        messages.error(request, 'Invalid coupon code')
    
    return redirect('shop:cart')


@login_required
def checkout(request):
    """Checkout process"""
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('shop:cart')
    
    shipping_addresses = request.user.addresses.filter(type='shipping')
    billing_addresses = request.user.addresses.filter(type='billing')
    shipping_methods = ShippingMethod.objects.filter(is_active=True)
    
    subtotal = cart.subtotal
    tax_amount = subtotal * Decimal('0.08')
    shipping_cost = Decimal('10.00')
    total_amount = subtotal + tax_amount + shipping_cost
    
    context = {
        'cart': cart,
        'shipping_addresses': shipping_addresses,
        'billing_addresses': billing_addresses,
        'shipping_methods': shipping_methods,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'shipping_cost': shipping_cost,
        'total_amount': total_amount,
    }
    
    return render(request, 'shop/checkout.html', context)


@login_required
@require_POST
def process_order(request):
    """Process the order"""
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        return JsonResponse({'success': False, 'error': 'Cart is empty'})
    
    try:
        shipping_address_id = request.POST.get('shipping_address')
        billing_address_id = request.POST.get('billing_address')
        payment_method = request.POST.get('payment_method')
        
        shipping_address = get_object_or_404(Address, id=shipping_address_id, user=request.user)
        billing_address = get_object_or_404(Address, id=billing_address_id, user=request.user)
        
        subtotal = cart.subtotal
        tax_amount = subtotal * Decimal('0.08')
        shipping_cost = Decimal('10.00')
        total_amount = subtotal + tax_amount + shipping_cost
        
        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_cost=shipping_cost,
            total_amount=total_amount,
            billing_address={
                'first_name': billing_address.first_name,
                'last_name': billing_address.last_name,
                'address_line_1': billing_address.address_line_1,
                'city': billing_address.city,
                'country': str(billing_address.country),
            },
            shipping_address={
                'first_name': shipping_address.first_name,
                'last_name': shipping_address.last_name,
                'address_line_1': shipping_address.address_line_1,
                'city': shipping_address.city,
                'country': str(shipping_address.country),
            }
        )
        
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.total_price,
                product_name=cart_item.product.title,
                product_sku=cart_item.variant.sku if cart_item.variant else cart_item.product.sku
            )
        
        Payment.objects.create(
            order=order,
            payment_id=f"order_{order.id}",
            method=payment_method,
            amount=total_amount,
            gateway='manual'
        )
        
        cart.items.all().delete()
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'redirect_url': f'/shop/order/{order.id}/confirmation/'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
        'order_items': order.items.all()
    }
    return render(request, 'shop/order_confirmation.html', context)


@login_required
def wishlist_view(request):
    """Display user's wishlist"""
    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user,
        defaults={'name': 'My Wishlist'}
    )
    context = {
        'wishlist': wishlist,
        'wishlist_items': wishlist.items.select_related('product').all()
    }
    return render(request, 'shop/wishlist.html', context)


@login_required
@require_POST
def add_to_wishlist(request):
    """Add product to wishlist"""
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id')
    
    product = get_object_or_404(ProductPage, id=product_id)
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id)
    
    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user,
        defaults={'name': 'My Wishlist'}
    )
    
    wishlist_item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product,
        variant=variant
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.title} added to wishlist' if created else 'Already in wishlist'
        })
    
    message = f'{product.title} added to wishlist' if created else 'Already in wishlist'
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'shop:wishlist'))


@login_required
def account_dashboard(request):
    """User account dashboard"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'recent_orders': recent_orders,
    }
    return render(request, 'shop/account_dashboard.html', context)


@login_required
def manage_addresses(request):
    """Manage user addresses"""
    addresses = request.user.addresses.all().order_by('-is_default', 'type')
    
    context = {
        'addresses': addresses
    }
    return render(request, 'shop/manage_addresses.html', context)