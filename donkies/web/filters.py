import django_filters


class CaseInsensitiveBooleanFilter(django_filters.Filter):
    """
    By default Boolean Filter work with pythonic True/False,
    but in Javascript: true/false.
    This custom filter resolve to be able use: true/false.
    """
    def filter(self, qs, value):
        if value is not None:
            lc_value = value.lower()
            if lc_value == 'true':
                value = True
            elif lc_value == 'false':
                value = False
            return qs.filter(**{self.name: value})
        return qs
