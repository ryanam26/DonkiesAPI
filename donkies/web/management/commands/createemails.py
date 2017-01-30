from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _
from web.models import Email


class Command(BaseCommand):
    def create_signup(self):
        e = Email(code=Email.SIGNUP)
        e.name = _('signup confirm')
        e.subject = _('Confirm registration')
        e.txt = 'file'
        e.html = 'file'
        e.save()

    def create_reset_password(self):
        e = Email(code=Email.RESET_PASSWORD)
        e.name = _('Reset password')
        e.subject = _('Reset password')
        e.txt = 'file'
        e.html = 'file'
        e.save()

    def create_resend_reg_confirmation(self):
        e = Email(code=Email.RESEND_REG_CONFIRMATION)
        e.name = 'Confirm registration'
        e.subject = 'Confirm registration'
        e.txt = 'file'
        e.html = 'file'
        e.save()

    def create_change_email(self):
        e = Email(code=Email.CHANGE_EMAIL)
        e.name = _('Change email')
        e.subject = _('Change email')
        e.txt = 'file'
        e.html = 'file'
        e.save()

    def handle(self, *args, **options):
        self.create_signup()
        self.create_reset_password()
        self.create_change_email()
        self.create_resend_reg_confirmation()
        print('Emails have been created.')
