from rest_framework import serializers
from finance.models import (
    Account, Institution, Item, Transaction,
    TransferDonkies, TransferPrepare, TransferUser, TransferDebt)


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = (
            'id',
            'plaid_id',
            'name',
            'has_mfa'
        )


class ItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='institution.name')

    class Meta:
        model = Item
        fields = (
            'id',
            'plaid_id',
            'institution',
            'name'
        )


class AccountSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    institution = serializers.SerializerMethodField()
    account_number = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
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
            'is_dwolla_created',
            'is_active',
            'institution',
            'item',
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
