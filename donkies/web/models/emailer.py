import copy
import datetime
from django.db import models
from django.contrib import admin
from django.conf import settings
from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.template import Context


class EmailerManager(models.Manager):
    def get_common_context(self):
        return {'domain': settings.FRONTEND_DOMAIN}

    def change_email_context(self, **kwargs):
        d = self.get_common_context()
        d['link_href'] = kwargs['user'].get_change_email_link()
        d['link_text'] = _('Confirm new email')
        return d

    def resend_reg_confirmation_context(self, **kwargs):
        d = self.get_common_context()
        d['link_href'] = kwargs['user'].get_confirmation_link()
        d['link_text'] = _('Confirm registration')
        return d

    def reset_password_context(self, **kwargs):
        d = self.get_common_context()
        d['link_href'] = kwargs['user'].get_reset_link()
        d['link_text'] = _('Reset password')
        return d

    def signup_context(self, **kwargs):
        d = self.get_common_context()
        d['link_href'] = kwargs['user'].get_confirmation_link()
        d['link_text'] = _('Verify')
        return d

    def process_email(self, code, **kwargs):
        """
        kwargs should have user object or
        email (email_to).
        """
        Email = apps.get_model('web', 'Email')
        try:
            email = Email.objects.get(code=code)
        except Email.DoesNotExist:
            raise ValidationError('Wrong code')

        txt = email.get_txt_template()
        html = email.get_html_template()

        d = copy.deepcopy(kwargs)
        addtitional_context = getattr(
            self, '{}_context'.format(email.code), None)
        if addtitional_context is not None:
            d.update(addtitional_context(**kwargs))

        if 'user' in kwargs:
            email_to = kwargs['user'].email
        else:
            email_to = kwargs['email']

        ctx = Context(d)
        em = self.model(
            email_to=email_to,
            email_from=settings.DEFAULT_FROM_EMAIL,
            subject=email.subject,
            html=html.render(ctx),
            txt=txt.render(ctx)
        )
        em.save()
        return em


class Emailer(models.Model):
    email_to = models.EmailField(max_length=100)
    email_from = models.EmailField(max_length=100)
    subject = models.CharField(max_length=255)
    txt = models.TextField()
    html = models.TextField()
    report = models.TextField(default='')
    sent = models.BooleanField(default=False)
    result = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    objects = EmailerManager()

    def __str__(self):
        return str(self.id)

    class Meta:
        app_label = 'web'
        verbose_name = 'email report'
        verbose_name_plural = 'email reports'
        ordering = ['-created_at']


@admin.register(Emailer)
class EmailerAdmin(admin.ModelAdmin):
    list_filter = ('result',)
    list_display = (
        'created_at',
        'sent_at',
        'email_to',
        'email_from',
        'subject',
        'result',
        'sent'
    )
    exclude = ('report', 'sent', 'result')

    def changelist_view(self, request, extra_context=None):
        # Delete rows that older than two weeks
        dt = datetime.date.today() - datetime.timedelta(days=14)

        Emailer.objects.filter(sent=True, sent_at__lt=dt).delete()
        return super().changelist_view(request, extra_context)

    def has_add_permission(self, request):
        return False
