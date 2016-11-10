from django.db import models
from django import forms


class TextareaXL(forms.Textarea):

    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        attrs.setdefault('cols', 140)
        attrs.setdefault('rows', 50)
        super(TextareaXL, self).__init__(*args, **kwargs)


class CharFieldWithTextarea(models.CharField):
    def formfield(self, **kwargs):
        kwargs.update({'widget': forms.Textarea})
        return super(CharFieldWithTextarea, self).formfield(**kwargs)
