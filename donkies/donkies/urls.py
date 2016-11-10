from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url('', include('social.apps.django_app.urls', namespace='social')),
    # url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^', include('web.urls')),
]

admin.site.site_header = 'donkies'
admin.site.site_title = 'donkies'
