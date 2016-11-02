from rest_framework import serializers
from donkiesoauth2.models import DonkiesUser


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = DonkiesUser
        fields = ('email',)
