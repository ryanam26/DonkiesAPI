import datetime
from django.db import models
from django.contrib import admin
from django.conf import settings
from django.apps import apps
from django.core.exceptions import ValidationError
from django.template import Template, Context


class EmailerManager(models.Manager):
    def mail_user(self, user, code):
        """
        code: list Email.CODE_CHOICES
        """
        Email = apps.get_model('web', 'Email')
        try:
            email = Email.objects.get(code=code)
        except Email.DoesNotExist:
            raise ValidationError('Wrong code')

        txt = Template(email.txt)
        html = Template(email.html)

        ctx = Context({'user': user})
        em = self.model(
            email_to=user.email,
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
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'
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
