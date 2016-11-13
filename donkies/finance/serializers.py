from rest_framework import serializers
from finance.models import (
    Account, Credentials, Institution, Member, Transaction)


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
        )


class CredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credentials
        fields = (
        )


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = (
        )


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = (
        )


class MemberCreateSerializer(serializers.ModelSerializer):
    institution_code = serializers.CharField()
    credentials = serializers.JSONField()

    class Meta:
        model = Member
        fields = (
            'institution_code',
            'credentials'
        )

    def convert_credentials(self, code, credentials):
        """
        Frontend send credentials as list of [{field_name:..., value: ...},]
        Convert them to: [{guid:..., value: ...},]
        """
        l = []
        for dic in credentials:
            try:
                cr = Credentials.objects.get(
                    institution__code=code, field_name=dic['field_name'])
            except Credentials.DoesNotExist:
                raise serializers.ValidationError('Incorrect credentials.')

            l.append({'guid': cr.guid, 'value': dic['value']})
        return l

    def validate(self, data):
        code = data['institution_code']
        data['credentials'] = self.convert_credentials(
            code, data['credentials'])
        return data

    def save(self, user):
        data = self.validated_data
        code = data['institution_code']
        credentials = data['credentials']
        m = Member.objects.get_or_create_member(user.guid, code, credentials)
        return m


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
        )
