from django.core.exceptions import ValidationError
from rest_framework import serializers
from finance.models import (
    Account, Institution, Transaction,
    TransferDonkies, TransferPrepare, TransferUser, TransferDebt)


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
    # member = MemberSerializer()
    institution = serializers.SerializerMethodField()
    account_number = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
            'uid',
            # 'member',
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
            'is_active',
            'institution',
            'account_number'
        )

    def get_institution(self, obj):
        i = obj.item.institution
        return InstitutionSerializer(i).data

    def get_account_number(self, obj):
        """
        Return last 4 digits/letters.
        """
        if obj.account_number is None:
            return None
        return obj.account_number[-4:]


class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.CharField(source='account.name', read_only=True)

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


class TransferDebtSerializer(serializers.ModelSerializer):
    account = serializers.CharField(source='account.name', read_only=True)
    created_at = serializers.DateTimeField(
        source='tu.created_at', read_only=True)

    class Meta:
        model = TransferDebt
        fields = (
            'id',
            'account',
            'amount',
            'share',
            'created_at',
            'processed_at',
            'is_processed'
        )


class TransferDonkiesSerializer(serializers.ModelSerializer):
    account = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = TransferDonkies
        fields = (
            'id',
            'account',
            'amount',
            'status',
            'sent_at',
            'is_sent'
        )


class TransferPrepareSerializer(serializers.ModelSerializer):
    account = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = TransferPrepare
        fields = (
            'id',
            'account',
            'roundup',
            'created_at'
        )


class TransferUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferUser
        fields = (
            'id',
            'user',
            'amount',
            'cached_amount',
            'created_at',
        )
