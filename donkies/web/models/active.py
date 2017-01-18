from django.db import models


class ActiveQuerySet(models.QuerySet):
    def delete(self):
        self.update(is_active=False)


class ActiveManager(models.Manager):
    def active(self):
        return self.model.objects.filter(is_active=True)

    def get_queryset(self):
        return ActiveQuerySet(self.model, using=self._db)


class ActiveModel(models.Model):
    """
    is_active state instead of deleting.
    """
    is_active = models.BooleanField(default=True, editable=False)

    class Meta:
        abstract = True

    def delete(self):
        self.is_active = False
        self.save()

    objects = ActiveManager()
