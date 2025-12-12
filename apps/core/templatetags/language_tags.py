from django import template

register = template.Library()

@register.simple_tag
def get_language_name(code):
    """Get language display name from code"""
    languages = {
        'en': 'English',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
        'it': 'Italiano',
    }
    return languages.get(code, 'English')
