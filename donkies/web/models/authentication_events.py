from django.db import models
from django.contrib import admin


class AuthenticationEvent(models.Model):
    is_success = models.BooleanField()
    ip_address = models.GenericIPAddressField()
    auth_datetime = models.DateTimeField(auto_now_add=True)
    user_attempted = models.ForeignKey('User', related_name='user_attempted', on_delete=models.CASCADE, default=None, blank=True, null=True)

    def __str__(self):
        return self.ip_address


@admin.register(AuthenticationEvent)
class AuthenticationEventAdmin(admin.ModelAdmin):
    list_display = (
        'is_success',
        'ip_address',
        'auth_datetime'
    )