from django.db import models
from django.contrib import admin
from django.apps import apps
from django.contrib.postgres.fields import JSONField
from finance.services.atrium_api import AtriumApi


class MemberManager(models.Manager):
    def create_member(self, api_response):
        """
        api_response is dictionary with response result.
        """
        User = apps.get_model('web', 'User')
        Institution = apps.get_model('finance', 'Institution')

        d = api_response
        d['user'] = User.objects.get(guid=d.pop('user_guid'))
        d['institution'] = Institution.objects.get(
            code=d.pop('institution_code'))

        m = self.model(**d)
        m.save()
        return m

    def get_or_create_member(self, user_guid, code, credentials):
        """
        TODO: Check that all required credentials of institution are passed.
              Processing errors.
        """
        Member = apps.get_model('finance', 'Member')

        # Check if member exists
        qs = Member.objects.filter(
            institution__code=code, user__guid=user_guid)
        if qs.exists():
            return qs.first()

        a = AtriumApi()
        result = a.create_member(user_guid, code, credentials)
        m = self.create_member(result)
        return m

    def get_status(self, member):
        """
        Returns status of the member.
        """
        a = AtriumApi()
        member = a.get_member(member.user.guid, member.guid)
        return member.status


class Member(models.Model):
    INITIATED = 'INITIATED'
    REQUESTED = 'REQUESTED'
    CHALLENGED = 'CHALLENGED'
    RECEIVED = 'RECEIVED'
    TRANSFERRED = 'TRANSFERRED'
    PROCESSED = 'PROCESSED'
    COMPLETED = 'COMPLETED'
    PREVENTED = 'PREVENTED'
    DENIED = 'DENIED'
    HALTED = 'HALTED'

    STATUS_CHOICES = [
        (INITIATED, 'initiated'),
        (REQUESTED, 'requested'),
        (CHALLENGED, 'challenged'),
        (RECEIVED, 'received'),
        (TRANSFERRED, 'transferred'),
        (PROCESSED, 'processed'),
        (COMPLETED, 'completed'),
        (PREVENTED, 'prevented'),
        (DENIED, 'denied'),
        (HALTED, 'halted')
    ]

    user = models.ForeignKey('web.User')
    institution = models.ForeignKey('Institution')
    guid = models.CharField(max_length=100, unique=True)
    identifier = models.CharField(
        max_length=50, null=True, default=None, blank=True)
    name = models.CharField(
        max_length=50, null=True, default=None, blank=True)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=INITIATED)
    aggregated_at = models.DateTimeField(
        null=True, default=None, blank=True)
    successfully_aggregated_at = models.DateTimeField(
        null=True, default=None, blank=True)
    metadata = JSONField(null=True, default=None)

    objects = MemberManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'member'
        verbose_name_plural = 'members'
        ordering = ['user']
        unique_together = ['user', 'institution']

    def __str__(self):
        if self.name:
            return self.name
        return self.guid


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'show_name',
        'user',
        'institution',
        'status',
        'aggregated_at',
        'successfully_aggregated_at'
    )

    def show_name(self, obj):
        if obj.name:
            return obj.name
        return obj.guid
    show_name.short_description = 'name'
