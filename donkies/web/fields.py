import base64
import pickle

from django.db import models
from django.db.models.fields import BooleanField, CharField


class LowerCharField(CharField):
    """
    To create LowerCharField - set lowercase=True in field.
    """
    def __init__(self, *args, **kwargs):
        self.is_lowercase = kwargs.pop('lowercase', False)
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is not None and self.is_lowercase:
            return value.lower()
        return value

    def from_db_value(self, value, expression, connection, context):
        return value

    def to_python(self, value):
        return value


class UniqueBooleanField(BooleanField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        objects = model_instance.__class__.objects
        # If True then set all others as False
        if getattr(model_instance, self.attname):
            objects.update(**{self.attname: False})
        # If no true object exists that isnt saved model, save as True
        elif not objects.exclude(id=model_instance.id)\
                        .filter(**{self.attname: True}):
            return True
        return getattr(model_instance, self.attname)


class ListField(models.TextField):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def get_prep_value(self, value):
        """
        Prepare to save in db.
        Should always return string.
        """
        if not value:
            return ''
        value = base64.b64encode(pickle.dumps(value))
        return value.decode()

    def from_db_value(self, value, expression, connection, context):
        if value is None or value == '':
            return []
        return self.parse_value(value)

    def to_python(self, value):
        """
        to_python() is called by deserialization and during
        the clean() method used from forms.

        As a general rule, to_python() should deal gracefully
        with any of the following arguments:
            1) An instance of the correct type
            2) A string
            3) None (if the field allows null=True)
        """
        if isinstance(value, list):
            return value

        if value is None or value == '':
            return []

        return self.parse_value(value)

    def parse_value(self, value):
        return pickle.loads(base64.b64decode(value))
