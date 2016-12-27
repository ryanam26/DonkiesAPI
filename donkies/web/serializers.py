from rest_framework import serializers
from web.models import User
from django.contrib import auth
from web.exceptions import PasswordsNotMatch


class EncIdMixin:
    def validate_encrypted_id(self, value):
        if not User.objects.filter(encrypted_id=value).exists():
            raise serializers.ValidationError(
                'Provided id is not correct')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password1 = serializers.CharField(min_length=8, max_length=30)
    new_password2 = serializers.CharField(min_length=8, max_length=30)

    def validate_current_password(self, value):
        email = self.context['request'].user.email
        user = auth.authenticate(
            email=email, password=value)
        if user is None:
            raise serializers.ValidationError(
                'Current password is not correct.')
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise PasswordsNotMatch('Passwords do not match.')

        return data

    def save(self):
        data = self.validated_data
        u = self.context['request'].user
        u.set_password(data['new_password1'])
        u.save()


class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()

    def save(self):
        data = self.validated_data
        u = self.context['request'].user
        u.change_email_request(data['new_email'])


class LoginSerializer(serializers.ModelSerializer):
    message = 'Email or password is not correct.'

    email = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'email',
            'password'
        )

    def validate(self, data):
        email = data['email']
        password = data['password']

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError(self.message)

        user = auth.authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError(self.message)

        return data


class PasswordResetRequireSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email is not correct')
        return value


class PasswordResetSerializer(EncIdMixin, serializers.Serializer):
    encrypted_id = serializers.CharField()
    reset_token = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        user = User.objects.get(encrypted_id=data['encrypted_id'])
        if user.reset_token != data['reset_token']:
            raise serializers.ValidationError(
                'Provided reset token is not correct')
        return data


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'first_name',
            'last_name',
        )

    def save(self):
        data = self.validated_data
        user = User.objects.create_user(data['email'], data['password'])
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.save()

        # Post save operations, send email e.t.c
        user.signup()


class SignupConfirmSerializer(EncIdMixin, serializers.Serializer):
    encrypted_id = serializers.CharField()
    confirmation_token = serializers.CharField()

    def validate(self, data):
        user = User.objects.get(encrypted_id=data['encrypted_id'])
        if user.is_confirmed:
            raise serializers.ValidationError(
                'Registration already has been confirmed.')

        if user.confirmation_token != data['confirmation_token']:
            raise serializers.ValidationError(
                'Provided confirmation token is not correct')
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'guid',
            'identifier',
            'email',
            'encrypted_id',
            'is_confirmed',
            'first_name',
            'last_name',
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
            'id',
            'guid',
            'identifier',
            'email',
            'encrypted_id',
            'is_confirmed',
        )
