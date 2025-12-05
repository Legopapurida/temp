from django import template
from apps.shop.models import ShopIndexPage

register = template.Library()


@register.simple_tag
def get_shop_url():
    """Get the URL of the first ShopIndexPage"""
    shop_page = ShopIndexPage.objects.live().first()
    return shop_page.url if shop_page else '/shop/'
