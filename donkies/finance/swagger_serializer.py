from rest_framework import serializers


class AccountsSetNumberSwaggerSerializer(serializers.Serializer):
    account_number = serializers.IntegerField()


class ItemSwaggerSerializer(serializers.Serializer):
    public_token = serializers.CharField(max_length=150)
    metadata_account_id = serializers.CharField(max_length=150)
