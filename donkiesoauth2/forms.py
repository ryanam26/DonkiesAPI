from django import forms
from donkiesoauth2.models import DonkiesUser


class DevUserRegForm(forms.ModelForm):
    class Meta:
        model = DonkiesUser
        exclude = ('is_developer', )
