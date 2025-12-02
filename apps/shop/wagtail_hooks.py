from wagtail import hooks
from wagtail.admin import widgets as wagtail_widgets
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from .models import Order, Payment, ProductReview, LoyaltyTransaction


# Register key models as snippets for easy admin access
register_snippet(Order)
register_snippet(Payment) 
register_snippet(ProductReview)
register_snippet(LoyaltyTransaction)


@hooks.register('construct_main_menu')
def add_ecommerce_menu_item(request, menu_items):
    """Add e-commerce menu items"""
    from wagtail.admin.menu import MenuItem
    
    menu_items.extend([
        MenuItem('Orders', '/admin/snippets/shop/order/', icon_name='doc-full'),
        MenuItem('Payments', '/admin/snippets/shop/payment/', icon_name='success'),
        MenuItem('Reviews', '/admin/snippets/shop/productreview/', icon_name='comment'),
        MenuItem('Loyalty Points', '/admin/snippets/shop/loyaltytransaction/', icon_name='star'),
    ])