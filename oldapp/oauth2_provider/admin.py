from django.contrib import admin

from .models import Grant, AccessToken, RefreshToken, get_application_model


class ApplicationAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)


class GrantAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('code', 'user',)


class AccessTokenAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('token', 'user',)


class RefreshTokenAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('token', 'user',)


Application = get_application_model()

admin.site.register(Application, ApplicationAdmin)
admin.site.register(Grant, GrantAdmin)
admin.site.register(AccessToken, AccessTokenAdmin)
admin.site.register(RefreshToken, RefreshTokenAdmin)
