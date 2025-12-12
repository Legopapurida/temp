from django import template

register = template.Library()


@register.simple_tag
def get_page_translations(page):
    return page.get_translations(inclusive=True)
