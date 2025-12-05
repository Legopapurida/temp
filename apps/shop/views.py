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
from django.db import models


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
    try:
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'cart_subtotal': float(cart.subtotal),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


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
def order_history(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'shop/order_history.html', {'page_obj': page_obj})


@login_required
def order_detail(request, order_id):
    """Order detail page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'order_items': order.items.all(),
        'shipments': order.shipments.all()
    }
    
    return render(request, 'shop/order_detail.html', context)


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


@require_POST
def remove_from_wishlist(request):
    """Remove item from wishlist"""
    item_id = request.POST.get('item_id')
    
    if request.user.is_authenticated:
        try:
            wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
            wishlist_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Item removed from wishlist'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Not authenticated'})


@login_required
def account_dashboard(request):
    """User account dashboard"""
    from apps.community.models import UserProfile as CommunityProfile
    
    profile, created = CommunityProfile.objects.get_or_create(user=request.user)
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


@login_required
def add_address(request):
    """Add new address"""
    from .forms import AddressForm
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('shop:manage_addresses')
    else:
        form = AddressForm()
    
    return render(request, 'shop/add_address.html', {'form': form})


@login_required
def edit_address(request, address_id):
    """Edit address"""
    from .forms import AddressForm
    
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('shop:manage_addresses')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'shop/edit_address.html', {'form': form, 'address': address})


@login_required
def delete_address(request, address_id):
    """Delete address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully!')
    return redirect('shop:manage_addresses')


@login_required
@require_POST
def add_review(request, product_id):
    """Add product review"""
    from .forms import ProductReviewForm
    
    product = get_object_or_404(ProductPage, id=product_id)
    
    # Check if user has purchased this product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status='delivered'
    ).exists()
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_verified_purchase = has_purchased
            review.save()
            messages.success(request, 'Review added successfully!')
            return redirect(product.url)
    
    return redirect(product.url)


@login_required
def edit_profile(request):
    """Edit user profile"""
    from .forms import UserProfileForm, UserForm
    
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('shop:account_dashboard')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'shop/edit_profile.html', context)


@login_required
def loyalty_points(request):
    """View loyalty points history"""
    transactions = LoyaltyTransaction.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    profile = getattr(request.user, 'shop_profile', None)
    
    context = {
        'page_obj': page_obj,
        'profile': profile
    }
    
    return render(request, 'shop/loyalty_points.html', context)


def calculate_shipping(request):
    """Calculate shipping cost via AJAX"""
    if request.method == 'POST':
        shipping_method_id = request.POST.get('shipping_method_id')
        
        try:
            shipping_method = ShippingMethod.objects.get(id=shipping_method_id)
            cart = get_or_create_cart(request)
            
            shipping_cost = shipping_method.calculate_cost(cart.total_weight, cart.subtotal)
            
            return JsonResponse({
                'success': True,
                'shipping_cost': float(shipping_cost)
            })
        except ShippingMethod.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid shipping method'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def remove_from_wishlist_ajax(request):
    """Remove item from wishlist via AJAX"""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
            product_name = wishlist_item.product.title
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'message': f'{product_name} removed from wishlist'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def product_reviews(request, product_id):
    """Display product reviews"""
    product = get_object_or_404(ProductPage, id=product_id)
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    
    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0,
        'total_reviews': reviews.count()
    }
    return render(request, 'shop/product_reviews.html', context)


def search_products(request):
    """Product search functionality"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    products = ProductPage.objects.live()
    
    if query:
        products = products.search(query)
    
    if category:
        products = products.filter(categories__name__icontains=category)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    context = {
        'products': products,
        'query': query,
        'category': category,
        'min_price': min_price,
        'max_price': max_price
    }
    return render(request, 'shop/search_results.html', context)


@login_required
def quick_add_to_cart(request):
    """Quick add to cart via AJAX"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(ProductPage, id=product_id)
        cart = get_or_create_cart(request)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'message': f'{product.title} added to cart'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})