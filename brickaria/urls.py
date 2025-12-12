from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponse

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from apps.core.views import SearchView

# Non-translatable URLs
urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('i18n/', include('django.conf.urls.i18n')),
    
    # Chrome DevTools
    path('.well-known/appspecific/com.chrome.devtools.json', lambda r: HttpResponse(status=204)),
]

# Translatable URLs with language prefix
urlpatterns += i18n_patterns(
    path('search/', SearchView.as_view(), name='search'),
    
    # App URLs
    path('games/', include('apps.games.urls')),
    path('shop/', include('apps.shop.urls')),
    path('community/', include('apps.community.urls')),
    path('events/', include('apps.events.urls')),
    path('support/', include('apps.support.urls')),
    
    # Custom accounts URLs (must come before allauth)
    path('accounts/', include('apps.accounts.urls')),
    
    # Authentication
    path('accounts/', include('allauth.urls')),
    
    # Wagtail pages (must be last)
    path('', include(wagtail_urls)),
)

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    
    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns