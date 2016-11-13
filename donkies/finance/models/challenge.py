from django.db import models
from django.contrib import admin
from django.apps import apps
from django.db import transaction


class ChallengeManager(models.Manager):
    @transaction.atomic
    def create_challenges(self, api_response):
        """
        Api response from atrium member detail endpoint.
        when member's status is CHALLENGED.
        Example: {
            'aggregated_at': '2016-11-13T17:00:25+00:00',
            'status': 'CHALLENGED',
            'guid': '***',
            'successfully_aggregated_at': None,
            'challenges': [
                {'label': 'What city were you born in?',
                'guid': '***',
                'type': 'TEXT',
                'field_name': None}
            ]
        }
        """
        for d in api_response['challenges']:
            self.get_or_create_challenge(api_response['guid'], **d)

    def get_or_create_challenge(
            self, member_guid, guid, label, type, field_name=None):

        Member = apps.get_model('finance', 'Member')
        member = Member.objects.get(guid=member_guid)

        try:
            c = self.model.objects.get(guid=guid)
        except self.model.DoesNotExist:
            c = self.model(member=member, guid=guid)

        c.label = label
        c.type = type
        c.field_name = field_name
        c.save()


class Challenge(models.Model):
    member = models.ForeignKey('Member')
    guid = models.CharField(max_length=100, unique=True)
    field_name = models.CharField(
        max_length=255, null=True, default=None)
    label = models.CharField(max_length=255)
    type = models.CharField(max_length=255)

    objects = ChallengeManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'challenge'
        verbose_name_plural = 'challenges'
        ordering = ['member']

    def __str__(self):
        return self.guid


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = (
        'member',
        'guid',
        'field_name',
        'label',
        'type'
    )
