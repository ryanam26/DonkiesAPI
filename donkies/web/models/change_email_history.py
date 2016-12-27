from django.db import models
from django.contrib import admin


class ChangeEmailHistoryManager(models.Manager):
    def create(self, user, email_old, email_new):
        ceh = self.model(
            user=user, email_old=email_old, email_new=email_new)
        ceh.save()
        return ceh


class ChangeEmailHistory(models.Model):
    user = models.ForeignKey('User')
    email_old = models.CharField(max_length=255)
    email_new = models.CharField(max_length=255)
    dt = models.DateTimeField(auto_now_add=True)

    objects = ChangeEmailHistoryManager()

    class Meta:
        app_label = 'web'
        verbose_name = 'change email history'
        verbose_name_plural = 'change email history'
        ordering = ['-dt']

    def __str__(self):
        return '{} -> {}'.format(
            self.email_old, self.email_new)


@admin.register(ChangeEmailHistory)
class ChangeEmailHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_old', 'email_new')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
