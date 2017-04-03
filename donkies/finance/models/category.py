from django.db import models
from django.contrib import admin
from django.contrib.postgres.fields import JSONField


class CategoryManager(models.Manager):
    def create_category(self, api_data):
        d = api_data
        c = self.model(
            plaid_id=d['category_id'],
            hierarchy=d['hierarchy'],
            group=d['group'],
        )
        c.save()
        return c


class Category(models.Model):
    plaid_id = models.CharField(max_length=50)
    group = models.CharField(max_length=50)
    hierarchy = JSONField()

    objects = CategoryManager()

    class Meta:
        app_label = 'finance'
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        ordering = ['plaid_id']

    def __str__(self):
        return self.plaid_id


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'plaid_id',
        'group',
        'hierarchy',
    )
    readonly_fields = (
        'plaid_id',
        'group',
        'hierarchy',
    )
