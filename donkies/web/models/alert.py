from django.db import models
from django.contrib import admin
from django.conf import settings
from web.services.sparkpost_service import SparkPostService


class AlertManager(models.Manager):
    def create_alert(self, type, subject, message):
        a = self.model(
            type=type,
            subject=subject,
            message=message,
        )
        a.save()
        return a


class Alert(models.Model):
    EMAIL = 'email'

    TYPE_CHOICES = (
        (EMAIL, 'email'),
    )
    type = models.CharField(
        max_length=50, choices=TYPE_CHOICES, default=EMAIL)
    subject = models.CharField(max_length=100)
    message = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    objects = AlertManager()

    class Meta:
        app_label = 'web'
        verbose_name = 'alert'
        verbose_name_plural = 'alerts'
        ordering = ['-created_at']

    def __str__(self):
        return self.subject

    def send(self):
        """
        Currently only one type.
        """
        if self.type == Alert.EMAIL:
            self.send_email()

    def send_email(self):
        if self.is_processed:
            return

        if settings.PRODUCTION:
            email = settings.ALERTS_EMAIL
        else:
            email = 'vladigris@gmail.com'

        sps = SparkPostService()
        sps.send_email(
            email,
            self.subject,
            self.message,
            html=self.message)

        self.is_processed = True
        self.save()


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'subject',
        'message',
        'is_processed',
    )
