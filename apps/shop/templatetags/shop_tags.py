from django import template
from apps.shop.models import ShopIndexPage
from decimal import Decimal

register = template.Library()


@register.simple_tag
def get_shop_url():
    """Get the URL of the first ShopIndexPage"""
    shop_page = ShopIndexPage.objects.live().first()
    return shop_page.url if shop_page else '/shop/'


@register.filter
def currency_format(value, currency='USD'):
    """Format price with currency symbol"""
    if value is None:
        return ''
    
    try:
        value = Decimal(str(value))
    except:
        return value
    
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'CAD': 'CA$',
        'AUD': 'A$',
    }
    
    symbol = symbols.get(currency, currency)
    return f"{symbol}{value:,.2f}"


@register.filter
def convert_currency(value, target_currency='USD'):
    """Convert currency (simplified - use real exchange rates in production)"""
    if value is None:
        return value
    
    try:
        value = Decimal(str(value))
    except:
        return value
    
    # Simplified conversion rates (use real API in production)
    rates = {
        'USD': Decimal('1.00'),
        'EUR': Decimal('0.92'),
        'GBP': Decimal('0.79'),
        'CAD': Decimal('1.36'),
        'AUD': Decimal('1.52'),
    }
    
    rate = rates.get(target_currency, Decimal('1.00'))
    return value * rate
