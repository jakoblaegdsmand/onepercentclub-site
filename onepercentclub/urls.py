from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from .views import HomeView

from bluebottle.urls.core import urlpatterns as bb_urlpatterns

admin.autodiscover()

handler500 = 'onepercentclub.views.handler500'

#Put the members urls before the bluebottle urls
urlpatterns = patterns('',
    url(r'^api/users/', include('apps.members.urls.api')),
)

urlpatterns += bb_urlpatterns

urlpatterns += patterns('',

    url(r'^api/fund/', include('apps.fund.urlsapi')),
    url(r'^api/fundraisers/', include('apps.fundraisers.urlsapi')),
    url(r'^api/organizations/', include('apps.organizations.urlsapi')),
    url(r'^api/partners/', include('apps.partners.urlsapi')),

    url(r'^api/', include('apps.projects.urls.api')),


    # Homepage API urls
    url(r'^api/projects/', include('apps.projects.urls.api')),
    url(r'^api/homepage/', include('apps.homepage.urls.api')),
    url(r'^api/stats', include('apps.statistics.urlsapi')),

    # API for DocData Status Changed Notifications.
    url(r'^api/docdatastatuschanged/', include('apps.cowry_docdata.urlsapi')),
    url(r'^api/docdatastatuschangedlegacy/', include('apps.cowry_docdata_legacy.urlsapi')),

    # Needed for the self-documenting API in Django Rest Framework.
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^', include('django.conf.urls.i18n')),
)

urlpatterns += patterns('loginas.views',
    url(r"^login/user/(?P<user_id>.+)/$", "user_login", name="loginas-user-login"),
)

urlpatterns += i18n_patterns('',

    # account login/logout, password reset, and password change
    url(r'^accounts/', include('django.contrib.auth.urls')),

    url(r'social/', include('social_auth.urls')),

    # These URL's will be automatically prefixed with the locale (e.g. '/nl/')
    url(r'^$', HomeView.as_view(), name='home'),

    # Django Admin, docs and password reset
    url(r'^admin/password_reset/$', 'django.contrib.auth.views.password_reset', name='admin_password_reset'),
    url(r'^admin/password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Other modules that need URLs exposed
    url(r'^admin/utils/taggit-autocomplete/', include('taggit_autocomplete_modified.urls')),
    url(r'^admin/utils/tinymce/', include('tinymce.urls')),
    url(r'^admin/utils/admintools/', include('admin_tools.urls')),

    # account login/logout, password reset, and password change
    url(r'^accounts/', include('django.contrib.auth.urls', namespace='accounts')),

    # Project view that search engines will use.
    url(r'^projects/', include('apps.projects.urls.seo')),

    # Organization urls for downloading private documents
    url(r'^documents/', include('bluebottle.utils.urls.main')),
    url(r'^documents/', include('apps.organizations.urls')),

    # handlebar templates
    url(r'^templates/', include('apps.hbtemplates.urls')),

    # Urls for partner sites
    url(r'^pp/', include('apps.partners.urls'))

)

js_info_dict = {
    'packages': ('apps.accounts', 'apps.projects'),
}

urlpatterns += patterns('',
    (r'^js$', 'django.views.i18n.javascript_catalog'),
)

# Serve django-staticfiles (only works in DEBUG)
# https://docs.djangoproject.com/en/dev/howto/static-files/#serving-static-files-in-development
urlpatterns += staticfiles_urlpatterns()

# Serve media files (only works in DEBUG)
# https://docs.djangoproject.com/en/dev/howto/static-files/#django.conf.urls.static.static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
