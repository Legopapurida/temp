from wagtail import hooks
from wagtail.admin.menu import MenuItem


@hooks.register('construct_main_menu')
def add_support_menu_item(request, menu_items):
    """Add support menu items to Wagtail admin"""
    menu_items.append(
        MenuItem('Help Tickets', '/admin/snippets/support/helpticket/', icon_name='help')
    )
