from rest_framework import serializers
from finance.models import (
    Account, Institution, Item, Transaction, TransferPrepare)


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


class ItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='institution.name')

    class Meta:
        model = Item
        fields = (
            'id',
            'guid',
            'plaid_id',
            'institution',
            'name'
        )


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
            'is_primary',
            'is_active',
            'institution',
            'item',
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
