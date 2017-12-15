from finance.models import (Account, Institution, Item, Lender, Transaction,
                            TransferBalance, TransferCalculation,
                            TransferPrepare)
from finance.models.funding_source import FundingSource
from rest_framework import serializers


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'


class LenderSerializer(serializers.ModelSerializer):
    pk = serializers.ReadOnlyField()
    user_id = serializers.ReadOnlyField(source='user.pk')
    institution_name = serializers.ReadOnlyField(source='institution.name')

    class Meta:
        model = Lender
        fields = ('pk', 'user_id', 'institution_name', 'account_number')


class TransferBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferBalance
        fields = (
            'funding_source',
            'account',
            'amount',
            'currency',
            'created',
            'transfer_id',
            'status'
        )


class ItemPostSerializer(serializers.Serializer):
    public_token = serializers.CharField()


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
            'additional_info',
            'plaid_id',
            'pause',
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
            'access_token',
            'accounts',
            'is_active'
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


class PauseAccountSerializer(serializers.Serializer):
    plaid_id = serializers.CharField()
    pause = serializers.BooleanField(default=False)


class DeleteFundingSourceSerializer(serializers.Serializer):
    item_id = serializers.CharField()

    class Meta:
        fields = (
            'item_id'
        )
