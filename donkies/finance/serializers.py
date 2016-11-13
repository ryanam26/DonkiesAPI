from rest_framework import serializers
from finance.models import (
    Account, Challenge, Credentials, Institution, Member, Transaction)


class AccountSerializer(serializers.ModelSerializer):
    member = serializers.StringRelatedField()

    class Meta:
        model = Account
        fields = (
            'uid',
            'member',
            'name',
            'apr',
            'apy',
            'available_balance',
            'available_credit',
            'balance',
            'created_at',
            'day_payment_is_due',
            'is_closed',
            'credit_limit',
            'interest_rate',
            'last_payment',
            'last_payment_at',
            'matures_on',
            'minimum_balance',
            'minimum_payment',
            'original_balance',
            'payment_due_at',
            'payoff_balance',
            'started_on',
            'subtype',
            'total_account_value',
            'type',
            'updated_at'
        )


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = (
            'field_name',
            'label',
            'type'
        )


class CredentialsSerializer(serializers.ModelSerializer):
    institution = serializers.StringRelatedField()

    class Meta:
        model = Credentials
        fields = (
            'institution',
            'field_name',
            'label',
            'type'
        )


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = (
            'code',
            'name',
            'url'
        )


class MemberSerializer(serializers.ModelSerializer):
    institution = serializers.StringRelatedField()
    challenges = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = (
            'institution',
            'identifier',
            'name',
            'status',
            'aggregated_at',
            'successfully_aggregated_at',
            'metadata',
            'member_status',
            'challenges'
        )

    def get_challenges(self, obj):
        if obj.status == Member.CHALLENGED:
            qs = Challenge.objects.filter(member=obj)
            s = ChallengeSerializer(qs, many=True)
            return s.data
        return []


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


class MemberResumeSerializer(serializers.Serializer):
    challenges = serializers.JSONField()

    class Meta:
        fields = (
            'challenges',
        )

    def convert_challenges(self, challenges):
        """
        Frontend send challenges as list of [{label:..., value: ...},]
        Convert them to: [{guid:..., value: ...},]
        """
        l = []
        for dic in challenges:
            try:
                cr = Challenge.objects.get(
                    member=self.context['member'], label=dic['label'])
            except Challenge.DoesNotExist:
                raise serializers.ValidationError('Incorrect challenges.')

            l.append({'guid': cr.guid, 'value': dic['value']})
        return l

    def validate(self, data):
        data['challenges'] = self.convert_challenges(data['challenges'])
        return data


class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.CharField()

    class Meta:
        model = Transaction
        fields = (
            'account',
            'uid',
            'amount',
            'check_number',
            'category',
            'created_at',
            'date',
            'description',
            'is_bill_pay',
            'is_direct_deposit',
            'is_expense',
            'is_fee',
            'is_income',
            'is_overdraft_fee',
            'is_payroll_advance',
            'latitude',
            'longitude',
            'memo',
            'merchant_category_code',
            'original_description',
            'posted_at',
            'status',
            'top_level_category',
            'transacted_at',
            'type',
            'updated_at'
        )