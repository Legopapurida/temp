from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from apps.core.views import SearchView

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
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
    
    # Support/Helpdesk (commented out until helpdesk is properly configured)
    # path('helpdesk/', include('helpdesk.urls')),
    
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path('', include(wagtail_urls)),
]

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