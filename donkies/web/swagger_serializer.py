from rest_framework import serializers


class LoginSwaggerSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
