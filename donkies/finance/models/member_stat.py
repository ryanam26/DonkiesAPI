from django.db import models
from django.contrib import admin
from finance.services.atrium_api import AtriumApi


class MemberStatManager(models.Manager):
    def update_stat(self):
        a = AtriumApi()
        for user in a.get_users():
            for member in a.get_members(user['guid']):
                qs = self.model.objects.filter(guid=member['guid'])
                if not qs.exists():
                    stat = self.model(
                        user_guid=user['guid'], guid=member['guid'])
                    stat.save()


class MemberStat(models.Model):
    """
    Model that contains info what members exist in Atrium.
    Updated by celery task.
    """
    user_guid = models.CharField(max_length=50)
    guid = models.CharField(max_length=50)

    objects = MemberStatManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'member stat'
        verbose_name_plural = 'members stat'
        ordering = ['-id']

    def __str__(self):
        return self.guid


@admin.register(MemberStat)
class MemberStatAdmin(admin.ModelAdmin):
    list_display = ('user_guid', 'guid')
