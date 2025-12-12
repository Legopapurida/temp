from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import translation
from .models import UserProfile, Order, Payment, LoyaltyTransaction


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'shop_profile'):
        instance.shop_profile.save()


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """Handle order status changes"""
    if not created:
        # Send email notifications based on status
        if instance.status == 'shipped':
            send_order_shipped_email(instance)
        elif instance.status == 'delivered':
            send_order_delivered_email(instance)
            # Award loyalty points for delivered orders
            award_loyalty_points(instance)


@receiver(post_save, sender=Payment)
def payment_completed(sender, instance, created, **kwargs):
    """Handle payment completion"""
    if instance.status == 'completed' and instance.order.status == 'pending':
        # Update order status to paid
        instance.order.status = 'paid'
        instance.order.save()
        
        # Send order confirmation email
        send_order_confirmation_email(instance.order)


def send_order_confirmation_email(order):
    """Send order confirmation email"""
    # Get user language preference
    user_language = 'en'
    if hasattr(order.user, 'shop_profile'):
        user_language = order.user.shop_profile.language or 'en'
    
    # Activate user's language
    translation.activate(user_language)
    
    # Get user currency
    currency = 'USD'
    if hasattr(order.user, 'shop_profile'):
        currency = order.user.shop_profile.currency or 'USD'
    
    symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'CAD': 'CA$', 'AUD': 'A$'}
    symbol = symbols.get(currency, '$')
    
    subject = f'Order Confirmation - #{order.order_number}'
    message = f'''
    Dear {order.user.get_full_name() or order.user.username},
    
    Thank you for your order! Your order #{order.order_number} has been confirmed.
    
    Order Total: {symbol}{order.total_amount}
    
    We'll send you another email when your order ships.
    
    Best regards,
    The Brickaria Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=True,
    )
    
    translation.deactivate()


def send_order_shipped_email(order):
    """Send order shipped email"""
    user_language = 'en'
    if hasattr(order.user, 'shop_profile'):
        user_language = order.user.shop_profile.language or 'en'
    
    translation.activate(user_language)
    
    subject = f'Your Order Has Shipped - #{order.order_number}'
    message = f'''
    Dear {order.user.get_full_name() or order.user.username},
    
    Great news! Your order #{order.order_number} has been shipped.
    
    You can track your order using the tracking information provided.
    
    Best regards,
    The Brickaria Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=True,
    )
    
    translation.deactivate()


def send_order_delivered_email(order):
    """Send order delivered email"""
    user_language = 'en'
    if hasattr(order.user, 'shop_profile'):
        user_language = order.user.shop_profile.language or 'en'
    
    translation.activate(user_language)
    
    subject = f'Order Delivered - #{order.order_number}'
    message = f'''
    Dear {order.user.get_full_name() or order.user.username},
    
    Your order #{order.order_number} has been delivered!
    
    We hope you love your purchase. Don't forget to leave a review!
    
    You've earned {int(order.total_amount)} loyalty points for this order.
    
    Best regards,
    The Brickaria Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=True,
    )
    
    translation.deactivate()


def award_loyalty_points(order):
    """Award loyalty points for completed orders"""
    if hasattr(order.user, 'shop_profile'):
        points = int(order.total_amount * settings.LOYALTY_POINTS_PER_DOLLAR)
        
        # Add points to user profile
        order.user.shop_profile.loyalty_points += points
        
        # Update loyalty tier
        update_loyalty_tier(order.user.shop_profile)
        order.user.shop_profile.save()
        
        # Create loyalty transaction record
        LoyaltyTransaction.objects.create(
            user=order.user,
            type='earned',
            points=points,
            description=f'Order #{order.order_number}',
            order=order
        )


def update_loyalty_tier(profile):
    """Update user's loyalty tier based on points"""
    points = profile.loyalty_points
    
    if points >= settings.LOYALTY_TIERS['platinum']['min_points']:
        profile.loyalty_tier = 'platinum'
    elif points >= settings.LOYALTY_TIERS['gold']['min_points']:
        profile.loyalty_tier = 'gold'
    elif points >= settings.LOYALTY_TIERS['silver']['min_points']:
        profile.loyalty_tier = 'silver'
    else:
        profile.loyalty_tier = 'bronze'


@receiver(pre_save, sender=Order)
def generate_order_number(sender, instance, **kwargs):
    """Generate order number if not exists"""
    if not instance.order_number:
        import random
        import string
        instance.order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))