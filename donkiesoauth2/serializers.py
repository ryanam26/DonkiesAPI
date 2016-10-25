from rest_framework import serializers
from donkiesoauth2.models import DonkiesUser


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonkiesUser
        fields = ('username', 'password')
        write_only_fields = ('password',)
