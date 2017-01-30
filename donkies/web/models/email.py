import os
from django.db import models
from django.contrib import admin
from django.conf import settings
from django.template.loader import get_template


class Email(models.Model):
    CHANGE_EMAIL = 'change_email'
    RESEND_REG_CONFIRMATION = 'resend_reg_confirmation'
    RESET_PASSWORD = 'reset_password'
    SIGNUP = 'signup'

    CODE_CHOICES = (
        (CHANGE_EMAIL, 'change email'),
        (RESEND_REG_CONFIRMATION, 'resend registration confirmation'),
        (RESET_PASSWORD, 'reset password'),
        (SIGNUP, 'signup')
    )

    code = models.CharField(max_length=50, choices=CODE_CHOICES)
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    txt = models.TextField(default='', blank=True)
    html = models.TextField(default='', blank=True)

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

    @property
    def folder(self):
        return os.path.join(
            settings.BASE_DIR, 'donkies/web/templates/web/emails/')

    def get_txt_template(self):
        """
        Returns Django Template instance.
        The name of file should be equal to code.
        """
        file_path = '{}{}.txt'.format(self.folder, self.code)
        return get_template(file_path)

    def get_html_template(self):
        """
        Returns Django Template instance.
        The name of file should be equal to code.
        """
        file_path = '{}{}.html'.format(self.folder, self.code)
        return get_template(file_path)


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
    )
