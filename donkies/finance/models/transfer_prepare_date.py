from django.db import models
from django.contrib import admin


class TransferPrepareDate(models.Model):
    """
    Current rule for transfer: Transfer once a day.
    This model is help model to track "today's"
    user's transfer.

    As soon as TransferPrepare is made once a day
    for particular user, do not process this user
    current date (today).
    """
    user = models.ForeignKey('web.User')
    date = models.DateField(auto_now_add=True)

    class Meta:
        app_label = 'finance'
        verbose_name = 'transfer prepare data'
        verbose_name_plural = 'transfers prepare date'
        ordering = ['-date']

    def __str__(self):
        return '{}: {}'.format(self.date, self.user)


@admin.register(TransferPrepareDate)
class TransferPrepareDateAdmin(admin.ModelAdmin):
    list_display = ('date', 'user')
