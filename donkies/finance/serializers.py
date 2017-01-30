from django.core.exceptions import ValidationError
from rest_framework import serializers
from finance.models import (
    Account, Challenge, Credentials, Institution, LinkDebt, Member,
    Transaction)


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = (
            'id',
            'code',
            'name',
            'url'
        )


class AccountSerializer(serializers.ModelSerializer):
    member = serializers.StringRelatedField()
    institution = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
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
            'type_ds',
            'updated_at',
            'transfer_share',
            'is_funding_source_for_transfer',
            'is_dwolla_created',
            'institution'
        )

    def get_institution(self, obj):
        i = obj.member.institution
        return InstitutionSerializer(i).data


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = (
            'guid',
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


class LinkDebtSerializer(serializers.ModelSerializer):
    account = AccountSerializer()

    class Meta:
        model = LinkDebt
        fields = (
            'account',
            'share'
        )


class LinkDebtCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkDebt
        fields = (
            'account',
            'share'
        )

    def create(self, data):
        try:
            ld = LinkDebt.objects.create_link(data['account'], data['share'])
        except ValidationError as e:
            raise serializers.ValidationError(e)
        return ld


class MemberSerializer(serializers.ModelSerializer):
    institution = serializers.StringRelatedField()
    challenges = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = (
            'id',
            'institution',
            'identifier',
            'name',
            'status',
            'aggregated_at',
            'successfully_aggregated_at',
            'metadata',
            'status_info',
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

    def save(self, user):
        data = self.validated_data
        code = data['institution_code']
        credentials = data['credentials']
        m = Member.objects.get_or_create_member(user.guid, code, credentials)
        # In case recreate user
        m.status = Member.REQUESTED
        m.save()
        return m


class MemberResumeSerializer(serializers.Serializer):
    """
    Frontend send challenges as list of [{guid:..., value: ...},]
    """
    challenges = serializers.JSONField()

    class Meta:
        fields = (
            'challenges',
        )


class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.CharField()

    class Meta:
        model = Transaction
        fields = (
            'account',
            'account_id',
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
            'updated_at',
            'roundup'
        )
