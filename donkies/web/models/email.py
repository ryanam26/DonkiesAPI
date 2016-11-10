from django.db import models
from django.contrib import admin


class Email(models.Model):
    SIGNUP = 'signup'
    RESET_PASSWORD = 'reset_password'
    CHANGE_EMAIL = 'change_email'

    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    txt = models.TextField()
    html = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'web'
        verbose_name = 'email'
        verbose_name_plural = 'emails'
        ordering = ['code']

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.subject:
                self.subject = self.name
        super().save(*args, **kwargs)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'subject',
        'txt',
        'html'
    )
    list_editable = (
        'subject',
        'txt',
        'html'
    )
