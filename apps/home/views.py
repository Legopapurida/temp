from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.utils import translation
from wagtail.models import Page, Locale

LANGUAGE_SESSION_KEY = '_language'


def switch_language(request):
    lang_code = request.GET.get("lang")
    page_id = request.GET.get("page_id")

    if not lang_code:
        return HttpResponseBadRequest("Missing language parameter")

    translation.activate(lang_code)
    request.session[LANGUAGE_SESSION_KEY] = lang_code

    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        request.user.userprofile.language = lang_code
        request.user.shop_profile.language = lang_code
        request.user.userprofile.save(update_fields=['language'])
        request.user.shop_profile.save(update_fields=['language'])

    if page_id:
        try:
            page = Page.objects.get(id=page_id).specific
            locale = Locale.objects.get(language_code=lang_code)
            translated = page.get_translation_or_none(locale)
            if translated:
                return redirect(translated.url)
        except (Page.DoesNotExist, Locale.DoesNotExist):
            pass

    return redirect(f"/{lang_code}/" if lang_code != 'en' else "/")
