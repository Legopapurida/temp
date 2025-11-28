from .models import SocialMediaLink, PrivacyPolicyPage, TermsOfServicePage
from apps.shop.models import ProductCategory, Brand
from apps.games.models import GameCategory
from wagtail.models import Page


def footer_context(request):
    """Add footer-related context to all templates"""
    return {
        'social_links': SocialMediaLink.objects.all(),
        'privacy_page': PrivacyPolicyPage.objects.live().first(),
        'terms_page': TermsOfServicePage.objects.live().first(),
        'footer_brands': Brand.objects.all(),
        'footer_product_categories': ProductCategory.objects.all(),
        'footer_game_categories': GameCategory.objects.all(),
        'shop_index_page': Page.objects.filter(content_type__model='shopindexpage').live().first(),
        'games_index_page': Page.objects.filter(content_type__model='gamesindexpage').live().first(),
    }