from django.conf.urls import url
from django.contrib import admin
from .models import Account
from finance import views


def get_admin_urls(urls):
    def get_urls():
        my_urls = []

        l = [
            Account
        ]

        for model in l:
            for path, view_name in model.get_admin_urls():
                v = getattr(views, view_name)
                ptn = url(path, admin.site.admin_view(v))
                my_urls.append(ptn)
        return my_urls + urls
    return get_urls
admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls
