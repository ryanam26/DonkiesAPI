from rest_framework import serializers
from finance.models import (
    Account, Institution, Item, Transaction, TransferPrepare, TransferCalculation)

from finance.models.funding_source import FundingSource


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = (
            'id',
            'plaid_id',
            'name',
            'has_mfa',
            'address',
            'box',
            'link'
        )


class ItemPostSerializer(serializers.Serializer):
    public_token = serializers.CharField()
    account_id = serializers.CharField()


class FakeRoundupsSerilizer(serializers.Serializer):
    roundup = serializers.DecimalField(max_digits=5, decimal_places=2)


class CreateTransactionSerializer(serializers.Serializer):
    access_token = serializers.CharField()


class CreateAccountSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField()
    institution_id = serializers.IntegerField()

    class Meta:
        model = Account
        fields = (
            'institution_id',
            'account_number',
            'additional_info'
        )

    def save(self, user):
        d = self.validated_data
        d['user_id'] = user.id
        return Account.objects.create_manual_account(**d)


class CreateMultipleAccountSerializer(serializers.Serializer):
    accounts = serializers.ListField(child=serializers.JSONField())


class AccountsEditShareSerializer(serializers.Serializer):
    idN = serializers.IntegerField()


class AccountsSetActiveSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()


class AccountSerializer(serializers.ModelSerializer):
    institution = serializers.SerializerMethodField()
    account_number = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
            'item',
            'guid',
            'name',
            'official_name',
            'balance',
            'mask',
            'type',
            'type_ds',
            'subtype',
            'transfer_share',
            'is_funding_source_for_transfer',
            'is_primary',
            'is_active',
            'institution',
            'account_number',
            'additional_info'
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


class ItemSerializer(serializers.ModelSerializer):
    accounts = AccountSerializer(many=True)
    name = serializers.CharField(source='institution.name')

    class Meta:
        model = Item
        fields = (
            'id',
            'guid',
            'plaid_id',
            'institution',
            'name',
            'pause',
            'access_token',
            'accounts',
        )


class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = Transaction
        fields = (
            'account',
            'account_id',
            'guid',
            'amount',
            'date',
            'name',
            'transaction_type',
            'category',
            'category_id',
            'pending',
            'pending_transaction_id',
            'payment_meta',
            'location',
            'roundup',
            'is_processed',
        )


class TransferPrepareSerializer(serializers.ModelSerializer):
    account = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = TransferPrepare
        fields = (
            'id',
            'account',
            'roundup',
            'created_at',
            'is_processed',
            'processed_at'
        )


class FundingSourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = FundingSource
        fields = (
            'id',
            'user',
            'funding_sources_url',
        )


class TransferCalculationSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransferCalculation
        fields = (
            'id',
            'user',
            'roundup_sum',
            'total_roundaps',
            'min_amount',
        )


class SetMinValueSerializer(serializers.Serializer):
    min_value = serializers.CharField()


class MakeTransferSerializer(serializers.Serializer):
    amount = serializers.CharField()


class PauseItemsSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    pause = serializers.BooleanField(default=False)
