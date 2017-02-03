import uuid
from django.db import models
from django.contrib import admin
from django.apps import apps
from django.contrib.postgres.fields import JSONField
from finance.services.atrium_api import AtriumApi
from web.models import ActiveModel, ActiveManager


class MemberManager(ActiveManager):
    def get_or_create_member(self, user_guid, code, credentials):
        """
        Called from create member serializer.
        TODO: Processing errors.
        """
        Account = apps.get_model('finance', 'Account')
        Member = apps.get_model('finance', 'Member')

        # Check if member exists.
        # Even if it was deleted previously (is_active=False).
        qs = Member.objects.filter(
            institution__code=code, user__guid=user_guid)
        if qs.exists():
            member = qs.first()
            if not member.is_active:
                member.is_active = True
                member.save()

                Account.objects.filter(
                    member=member, is_active=False).update(is_active=True)
            return member

        a = AtriumApi()
        result = a.create_member(user_guid, code, credentials)
        m = self.create_member(result)
        return m

    def create_member(self, api_response):
        """
        api_response is dictionary with response result from Atrium.
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

    def get_atrium_members(self, user_guid):
        a = AtriumApi()
        return a.get_members(user_guid)

    def get_atrium_member(self, member):
        """
        Returns member data from atrium response.
        """
        a = AtriumApi()
        member = a.get_member(member.user.guid, member.guid)
        return member

    def resume_member(self, member_guid, challenges=[]):
        """
        Aggregates or resumes member.
        After that celery task for getting member should be called.
        """
        member = Member.objects.get(guid=member_guid)
        a = AtriumApi()
        a.resume_member(member.user.guid, member.guid, challenges)

    def delete_member(self, member_id, is_delete_atrium=True):
        """
        Set member, accounts and transactions to is_active=False
        Can delete member from Atrium.
        """
        Account = apps.get_model('finance', 'Account')
        Transaction = apps.get_model('finance', 'Transaction')

        member = self.model.objects.get(id=member_id)

        if is_delete_atrium:
            a = AtriumApi()
            a.delete_member(member.user.guid, member.guid)

        Account.objects.active().filter(member=member).update(is_active=False)
        Transaction.objects.active().filter(
            account__member=member).update(is_active=False)
        member.delete()


class Member(ActiveModel):
    SUCCESS = 'SUCCESS'
    PROCESSING = 'PROCESSING'
    ERROR = 'ERROR'

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

    PROCESSING_STATUSES = [
        INITIATED,
        REQUESTED,
        RECEIVED,
        TRANSFERRED,
        PROCESSED
    ]

    FINISHED_STATUSES = [
        CHALLENGED,
        COMPLETED,
        PREVENTED,
        DENIED,
        HALTED,
    ]

    user = models.ForeignKey('web.User')
    institution = models.ForeignKey('Institution')
    guid = models.CharField(max_length=100, unique=True)
    identifier = models.CharField(
        max_length=50, null=True, default=None, unique=True)
    name = models.CharField(
        max_length=50, null=True, default=None, blank=True)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=INITIATED)
    aggregated_at = models.DateTimeField(
        null=True, default=None, blank=True)
    successfully_aggregated_at = models.DateTimeField(
        null=True, default=None, blank=True)
    metadata = JSONField(null=True, default=None)
    is_created = models.BooleanField(default=False)

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

    @property
    def status_info(self):
        """
        Returns dict status for frontend.
        "name": PROCESSING / SUCCESS / ERROR / CHALLENGED
        """
        processing = [
            self.INITIATED,
            self.REQUESTED,
            self.RECEIVED,
            self.TRANSFERRED,
            self.PROCESSED
        ]
        if self.status in processing:
            return {
                'name': self.PROCESSING,
                'message': 'Processing...',
                'is_completed': False,
                'status': self.status
            }

        if self.status == self.CHALLENGED:
            return {
                'name': self.CHALLENGED,
                'message': 'Please provide additional info.',
                'is_completed': True,
                'status': self.status
            }

        if self.status == self.DENIED:
            return {
                'name': self.ERROR,
                'message': 'Incorrect credentials.',
                'is_completed': True,
                'status': self.status
            }

        if self.status == self.COMPLETED:
            return {
                'name': self.SUCCESS,
                'message': 'Bank account has been created!',
                'is_completed': True,
                'status': self.status
            }

        return {
            'name': self.ERROR,
            'message': 'Other error.',
            'is_completed': True,
            'status': self.status
        }

    def save(self, *args, **kwargs):
        if not self.pk:
            self.identifier = uuid.uuid4().hex

        if self.successfully_aggregated_at is not None:
            self.is_created = True
        super().save(*args, **kwargs)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'show_name',
        'user',
        'institution',
        'status',
        'aggregated_at',
        'successfully_aggregated_at',
        'is_active'
    )
    exclude = ('metadata',)

    def show_name(self, obj):
        if obj.name:
            return obj.name
        return obj.guid
    show_name.short_description = 'name'

    def has_delete_permission(self, request, obj=None):
        return False
