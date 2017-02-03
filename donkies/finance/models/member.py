import uuid
from django.db import models
from django.db import transaction
from django.contrib import admin
from django.apps import apps
from django.contrib.postgres.fields import JSONField
from finance.services.atrium_api import AtriumApi
from web.models import ActiveModel, ActiveManager


class MemberManager(ActiveManager):
    def get_or_create_member(self, user_guid, code, credentials):
        """
        1) Returns member, if it exists and is_active=True
        2) Reactivates member if it was deleted previously.
           When user delete member, member is deleted from Atrium,
           but it still exists in database. If user decided to create
           member for the same institution again, reactivate
           member with new Atrium guid.
        3) Creates new member if it doesn't exists.
        """
        member = None
        qs = self.model.objects.filter(
            institution__code=code, user__guid=user_guid)
        if qs.exists():
            member = qs.first()
            if member.is_active:
                return member

        # Create member in Atrium
        a = AtriumApi()
        result = a.create_member(user_guid, code, credentials)

        # Reactivate member
        if member is not None:
            self.change_active(member.id, True)
            member.guid = result['guid']
            member.save()
            return member

        # Create new member.
        member = self.create_member(result)
        return member

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
        member = self.model.objects.get(id=member_id)

        if is_delete_atrium:
            a = AtriumApi()
            a.delete_member(member.user.guid, member.guid)

        self.change_active(member.id, False)

    @transaction.atomic
    def change_active(self, member_id, is_active):
        """
        is_active = True - besides member itself,
                    activates also all accounts.
        is_active = False - besides member itself,
                    deactivates also all accounts.
        """
        Account = apps.get_model('finance', 'Account')
        for account in Account.objects.filter(member_id=member_id):
            Account.objects.change_active(account.id, is_active)
        self.model.objects.filter(id=member_id).update(is_active=is_active)


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
