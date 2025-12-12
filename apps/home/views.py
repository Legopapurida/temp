from django.shortcuts import redirect
from django.utils import translation
from wagtail.models import Page, Locale
from django.http import HttpResponseBadRequest

LANGUAGE_SESSION_KEY = '_language'


def switch_language(request):
    lang_code = request.GET.get("lang")
    page_id = request.GET.get("page_id")

    if not lang_code:
        return HttpResponseBadRequest("Missing language parameter")

    translation.activate(lang_code)
    request.session[LANGUAGE_SESSION_KEY] = lang_code

    if page_id:
        try:
            page = Page.objects.get(id=page_id).specific
            locale = Locale.objects.get(language_code=lang_code)
            translated = page.get_translation_or_none(locale)
            if translated:
                return redirect(translated.url)
        except (Page.DoesNotExist, Locale.DoesNotExist):
            pass
    
    return redirect(f"/{lang_code}/")
