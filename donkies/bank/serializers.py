from rest_framework import serializers
from finance.serializers import AccountSerializer
from bank.models import Customer, FundingSource


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'ip_address',
            'type',
            'address1',
            'address2',
            'city',
            'state',
            'postal_code',
            'date_of_birth',
            'ssn',
            'phone',
            'id',
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
