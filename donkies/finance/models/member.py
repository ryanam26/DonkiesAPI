from django.db import models
from django.contrib import admin


class Member(models.Model):
    INITIATED = 'initiated'
    REQUESTED = 'requested'
    CHALLENGED = 'challenged'
    RECEIVED = 'received'
    TRANSFERRED = 'transferred'
    PROCESSED = 'processed'
    COMPLETED = 'completed'
    PREVENTED = 'prevented'
    DENIED = 'denied'
    HALTED = 'halted'

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

    class Meta:
        app_label = 'finance'
        verbose_name = 'member'
        verbose_name_plural = 'members'
        ordering = ['user']

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
