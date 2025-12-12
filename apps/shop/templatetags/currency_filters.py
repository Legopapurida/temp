from django import template
from decimal import Decimal

register = template.Library()

CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'CAD': 'CA$',
    'AUD': 'A$',
}

@register.filter
def format_price(product_or_amount, currency='USD'):
    """Format price with currency symbol"""
    from apps.shop.models import ProductPage, ProductVariant
    
    # If it's a product, get the price in the specified currency
    if isinstance(product_or_amount, (ProductPage, ProductVariant)):
        amount = product_or_amount.get_current_price(currency)
    else:
        amount = product_or_amount
    
    if not amount:
        amount = 0
    
    symbol = CURRENCY_SYMBOLS.get(currency, '$')
    return f"{symbol}{amount:.2f}"

@register.simple_tag
def get_price(product, currency='USD'):
    """Get product price in specified currency"""
    return product.get_price(currency)

@register.simple_tag
def get_sale_price(product, currency='USD'):
    """Get product sale price in specified currency"""
    return product.get_sale_price(currency)

@register.simple_tag
def get_current_price(product, currency='USD'):
    """Get product current price in specified currency"""
    return product.get_current_price(currency)

@register.filter
def currency_symbol(currency='USD'):
    """Get currency symbol"""
    return CURRENCY_SYMBOLS.get(currency, '$')
