import datetime
import uuid
from django.db import models
from django.contrib import admin
from django.conf import settings
from django.utils import timezone


class TokenManager(models.Manager):
    def create(self, user, expire_minutes=settings.TOKEN_EXPIRE_MINUTES):
        token = self.model(user=user)
        token.key = uuid.uuid4().hex
        if expire_minutes:
            now = timezone.now()
            token.expire_at = now + datetime.timedelta(minutes=expire_minutes)
        token.save()
        return token


class Token(models.Model):
    user = models.ForeignKey('User')
    key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField(null=True, blank=True, default=None)

    objects = TokenManager()

    class Meta:
        app_label = 'web'
        verbose_name = 'token'
        verbose_name_plural = 'tokens'
        ordering = ['-created_at']

    def __str__(self):
        return self.key


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'key',
        'created_at',
        'expire_at'
    )

    def has_add_permission(self, request, obj=None):
        return False
