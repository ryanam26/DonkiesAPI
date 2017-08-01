from rest_framework import serializers


class AccountsSetNumberSwaggerSerializer(serializers.Serializer):
    account_number = serializers.IntegerField()
