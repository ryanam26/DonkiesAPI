from rest_framework import serializers
from bank.models import Customer


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
