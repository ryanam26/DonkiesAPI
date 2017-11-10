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
    FUNDING_SOURCE_ADDED = 'funding_source_added'
    FUNDING_SOURCE_REMOVED = 'funding_source_removed'
    FUNDING_SOURCE_VERIFIED = 'funding_source_verified'
    MICRODEPOSITS_ADDED = 'microdeposits_added'
    MICRODEPOSITS_FAILED = 'microdeposits_failed'
    MICRODEPOSITS_COMPLETED = 'microdeposits_completed'
    MICRODEPOSITS_MAXATTEMPTS = 'microdeposits_maxattempts'
    BANK_TRANSFER_CREATED = 'bank_transfer_created'
    BANK_TRANSFER_CANCELLED = 'bank_transfer_cancelled'
    BANK_TRANSFER_FAILED = 'bank_transfer_failed'
    BANK_TRANSFER_COMPLETED = 'bank_transfer_completed'
    TRANSFER_CREATED = 'transfer_created'
    TRANSFER_CANCELLED = 'transfer_cancelled'
    TRANSFER_FAILED = 'transfer_failed'
    TRANSFER_RECLAIMED = 'transfer_reclaimed'
    TRANSFER_COMPLETED = 'transfer_completed'
    MASS_PAYMENT_CREATED = 'mass_payment_created'
    MASS_PAYMENT_COMPLETED = 'mass_payment_completed'
    MASS_PAYMENT_CANCELLED = 'mass_payment_cancelled'
    ACCOUNT_SUSPENDED = 'account_suspended'
    ACCOUNT_ACTIVATED = 'account_activated'
    CUSTOMER_CREATED = 'customer_created'
    CUSTOMER_VERIFICATION_DOCUMENT_NEEDED = 'customer_verification_document_needed'
    CUSTOMER_VERIFICATION_DOCUMENT_UPLOADED = 'customer_verification_document_uploaded'
    CUSTOMER_VERIFICATION_DOCUMENT_FAILED = 'customer_verification_document_failed'
    CUSTOMER_VERIFICATION_DOCUMENT_APPROVED = 'customer_verification_document_approved'
    CUSTOMER_REVERIFICATION_NEEDED = 'customer_reverification_needed'
    CUSTOMER_VERIFIED = 'customer_verified'
    CUSTOMER_SUSPENDED = 'customer_suspended'
    CUSTOMER_ACTIVATED = 'customer_activated'
    CUSTOMER_DEACTIVATED = 'customer_deactivated'
    CUSTOMER_FUNDING_SOURCE_ADDED = 'customer_funding_source_added'
    CUSTOMER_FUNDING_SOURCE_REMOVED = 'customer_funding_source_removed'
    CUSTOMER_FUNDING_SOURCE_VERIFIED = 'customer_funding_source_verified'
    CUSTOMER_MICRODEPOSITS_ADDED = 'customer_microdeposits_added'
    CUSTOMER_MICRODEPOSITS_FAILED = 'customer_microdeposits_failed'
    CUSTOMER_MICRODEPOSITS_COMPLETED = 'customer_microdeposits_completed'
    CUSTOMER_MICRODEPOSITS_MAXATTEMPTS = 'customer_microdeposits_maxattempts'
    CUSTOMER_BANK_TRANSFER_CREATED = 'customer_bank_transfer_created'
    CUSTOMER_BANK_TRANSFER_CANCELLED = 'customer_bank_transfer_cancelled'
    CUSTOMER_BANK_TRANSFER_FAILED = 'customer_bank_transfer_failed'
    CUSTOMER_BANK_TRANSFER_COMPLETED = 'customer_bank_transfer_completed'
    CUSTOMER_TRANSFER_CREATED = 'customer_transfer_created'
    CUSTOMER_TRANSFER_CANCELLED = 'customer_transfer_cancelled'
    CUSTOMER_TRANSFER_FAILED = 'customer_transfer_failed'
    CUSTOMER_TRANSFER_COMPLETED = 'customer_transfer_completed'
    CUSTOMER_MASS_PAYMENT_CREATED = 'customer_mass_payment_created'
    CUSTOMER_MASS_PAYMENT_COMPLETED = 'customer_mass_payment_completed'
    CUSTOMER_MASS_PAYMENT_CANCELLED = 'customer_mass_payment_cancelled'

    CODE_CHOICES = (
        (CHANGE_EMAIL, 'change email'),
        (RESEND_REG_CONFIRMATION, 'resend registration confirmation'),
        (RESET_PASSWORD, 'reset password'),
        (SIGNUP, 'signup'),
        (FUNDING_SOURCE_ADDED, 'funding source added'),
        (FUNDING_SOURCE_REMOVED, 'funding source removed'),
        (FUNDING_SOURCE_VERIFIED, 'funding source verified'),
        (MICRODEPOSITS_ADDED, 'microdeposits added'),
        (MICRODEPOSITS_FAILED, 'microdeposits failed'),
        (MICRODEPOSITS_COMPLETED, 'microdeposits completed'),
        (MICRODEPOSITS_MAXATTEMPTS, 'microdeposits maxattempts'),
        (BANK_TRANSFER_CREATED, 'bank transfer created'),
        (BANK_TRANSFER_CANCELLED, 'bank transfer cancelled'),
        (BANK_TRANSFER_FAILED, 'bank transfer failed'),
        (BANK_TRANSFER_COMPLETED, 'bank transfer completed'),
        (TRANSFER_CREATED, 'transfer created'),
        (TRANSFER_CANCELLED, 'transfer cancelled'),
        (TRANSFER_FAILED, 'transfer failed'),
        (TRANSFER_RECLAIMED, 'transfer reclaimed'),
        (TRANSFER_COMPLETED, 'transfer completed'),
        (MASS_PAYMENT_CREATED, 'mass payment created'),
        (MASS_PAYMENT_COMPLETED, 'mass payment completed'),
        (MASS_PAYMENT_CANCELLED, 'mass payment cancelled'),
        (ACCOUNT_SUSPENDED, 'account suspended'),
        (ACCOUNT_ACTIVATED, 'account activated'),
        (CUSTOMER_CREATED, 'customer created'),
        (CUSTOMER_VERIFICATION_DOCUMENT_NEEDED, 'customer verification document needed'),
        (CUSTOMER_VERIFICATION_DOCUMENT_UPLOADED, 'customer verification document uploaded'),
        (CUSTOMER_VERIFICATION_DOCUMENT_FAILED, 'customer verification document failed'),
        (CUSTOMER_VERIFICATION_DOCUMENT_APPROVED, 'customer verification document approved'),
        (CUSTOMER_REVERIFICATION_NEEDED, 'customer reverification needed'),
        (CUSTOMER_VERIFIED, 'customer verified'),
        (CUSTOMER_SUSPENDED, 'customer suspended'),
        (CUSTOMER_ACTIVATED, 'customer activated'),
        (CUSTOMER_DEACTIVATED, 'customer deactivated'),
        (CUSTOMER_FUNDING_SOURCE_ADDED, 'customer funding source added'),
        (CUSTOMER_FUNDING_SOURCE_REMOVED, 'customer funding source removed'),
        (CUSTOMER_FUNDING_SOURCE_VERIFIED, 'customer funding source verified'),
        (CUSTOMER_MICRODEPOSITS_ADDED, 'customer microdeposits added'),
        (CUSTOMER_MICRODEPOSITS_FAILED, 'customer microdeposits failed'),
        (CUSTOMER_MICRODEPOSITS_COMPLETED, 'customer microdeposits completed'),
        (CUSTOMER_MICRODEPOSITS_MAXATTEMPTS, 'customer microdeposits maxattempts'),
        (CUSTOMER_BANK_TRANSFER_CREATED, 'customer bank transfer created'),
        (CUSTOMER_BANK_TRANSFER_CANCELLED, 'customer bank transfer cancelled'),
        (CUSTOMER_BANK_TRANSFER_FAILED, 'customer bank transfer failed'),
        (CUSTOMER_BANK_TRANSFER_COMPLETED, 'customer bank transfer completed'),
        (CUSTOMER_TRANSFER_CREATED, 'customer transfer created'),
        (CUSTOMER_TRANSFER_CANCELLED, 'customer transfer cancelled'),
        (CUSTOMER_TRANSFER_FAILED, 'customer transfer failed'),
        (CUSTOMER_TRANSFER_COMPLETED, 'customer transfer completed'),
        (CUSTOMER_MASS_PAYMENT_CREATED, 'customer mass payment created'),
        (CUSTOMER_MASS_PAYMENT_COMPLETED, 'customer mass payment completed'),
        (CUSTOMER_MASS_PAYMENT_CANCELLED, 'customer mass payment cancelled')
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
