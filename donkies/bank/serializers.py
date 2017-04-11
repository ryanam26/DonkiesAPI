from rest_framework import serializers
from finance.serializers import AccountSerializer
from bank.models import (
    Customer, FundingSource, TransferDonkies, TransferUser, TransferDebt)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'id',
            'ip_address',
            'type',
            'dwolla_type',
            'dwolla_id',
            'status',
            'created_at'
        )

        read_only_fields = (
            'id',
            'dwolla_type',
            'dwolla_id',
            'status',
            'created_at'
        )

    def save(self, user):
        d = self.validated_data
        d['user'] = user
        c = Customer.objects.create_customer(**d)
        return c


class FundingSourceSerializer(serializers.ModelSerializer):
    account = AccountSerializer()

    class Meta:
        model = FundingSource
        fields = (
            'id',
            'account',
            'dwolla_id',
            'account_number',
            'routing_number',
            'status',
            'type',
            'typeb',
            'name',
            'created_at',
            'is_removed'
        )


class FundingSourceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingSource
        fields = (
            'account_number',
            'routing_number',
            'type',
            'name',
        )

    def save(self, account):
        d = self.validated_data
        d['account'] = account
        fs = FundingSource.objects.create_funding_source(**d)
        return fs


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
