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
            'phone'
        )

        read_only_fields = (
            'dwolla_type',
            'dwolla_id',
            'status',
            'created_at',
            'is_created'
        )

    def save(self, user):
        d = self.validated_data
        d['user'] = user
        c = Customer.objects.create_customer(**d)
        return c
