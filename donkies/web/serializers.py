from rest_framework import serializers
from web.models import User
from django.contrib import auth
from django.conf import settings
from web.exceptions import PasswordsNotMatch
from finance.serializers import (FundingSourceSerializer,
                                 TransferCalculationSerializer)
# from bank.serializers import CustomerSerializer
from django.apps import apps
from bank.services.dwolla_api import DwollaApi
import hashlib
from recaptcha.fields import ReCaptchaField


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


class FacebookAuthSerializer(serializers.Serializer):
    code = serializers.CharField()
    redirect_uri = serializers.CharField(required=False)
    rt_mode = serializers.BooleanField(required=False)

    def validate(self, data):
        """
        get_facebook_user method returns dict
        with id and email or raise error
        """
        if 'redirect_uri' in data:
            redirect_uri = data['redirect_uri']
        else:
            redirect_uri = settings.FACEBOOK_REDIRECT_URI

        dic = User.get_facebook_user(data['code'], redirect_uri)
        for k, v in dic.items():
            data[k] = v
        return data


class LoginSerializer(serializers.ModelSerializer):
    message = 'Email or password is not correct.'

    email = serializers.CharField()
    password = serializers.CharField()
    # recaptcha = ReCaptchaField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            # 'recaptcha'
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


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email not exists')
        return value


class CheckEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def check_email(self):
        user = User.objects.filter(email=self.data['email']).all()
        if user:
            return {'is_exist': True}
        return {'is_exist': False}


class UserUpdateFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'is_confirmed',
            'address1',
            'address2',
            'city',
            'state',
            'postal_code',
            'date_of_birth',
            'ssn',
            'phone',
            'is_profile_completed',
            'signup_steps',
            'is_paused',
        )


class PasswordResetSerializer(EncIdMixin, serializers.Serializer):
    encrypted_id = serializers.CharField()
    reset_token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate(self, data):
        try:
            user = User.objects.get(encrypted_id=data['encrypted_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Provided id is not correct')

        if user.reset_token != data['reset_token']:
            raise serializers.ValidationError(
                'Provided reset token is not correct')
        return data


class SignupParentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8)
    email_child = serializers.CharField(required=False)
    hash_user = serializers.CharField(required=False)
    id_user = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'password',
            'address1',
            'city',
            'state',
            'postal_code',
            'email_child',
            'hash_user',
            'id_user',
        )

    def save(self):
        data = self.validated_data
        user = User.objects.create_user(data['email'], data['password'])
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.address1 = data['address1']
        user.postal_code = data['postal_code']
        user.city = data['city']
        user.state = data['state']
        user.is_parent = True

        personal_string = 'id-{}_salt-{}'

        hash_user = data.get('hash_user', None)
        id_user = data.get('id_user', None)
        child_email = data.get('email_child', None)

        try:
            if hash_user and id_user is not None:
                m = hashlib.md5()
                id_user = int(id_user)
                child = User.objects.get(id=id_user)
                email = child.email

                personal_string = personal_string.format(id_user, settings.SALT)
                m.update(personal_string.encode())
                m_hash = m.hexdigest()

                if m_hash == hash_user:
                    child = User.objects.get(id=id_user, email=email)
                else:
                    raise Exception('hash not equal')
            elif child_email:
                child = User.objects.get(email=data['email_child'])
        except User.DoesNotExist as e:
            raise e

        child.child = user
        child.save()

        user.save()
        # Post save operations, send email e.t.c
        user.signup()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8)
    # recaptcha = ReCaptchaField(write_only=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'password',
            'address1',
            'postal_code',
            'city',
            'state',
            'date_of_birth',
            'ssn',
            'ipAddress',
            'type',
            'phone',
            # 'recaptcha'
        )

    def save(self):

        data = self.validated_data

        request_body = {
            'firstName': data['first_name'],
            'lastName': data['last_name'],
            'email': data['email'],
            'type': data['type'],
            'address1': data['address1'],
            'city': data['city'],
            'state': data['state'],
            'postalCode': data['postal_code'],
            'dateOfBirth': str(data['date_of_birth']),
            'ssn': data['ssn'],
            'phone': data['phone'],
        }

        dw = DwollaApi()

        try:
            id = dw.create_customer(request_body)
        except Exception as e:
            raise Exception(e)

        if id is not None:
            user = User.objects.create_user(data['email'], data['password'])
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.address1 = data['address1']
            user.postal_code = data['postal_code']
            user.city = data['city']
            user.state = data['state']
            user.date_of_birth = data['date_of_birth']
            user.phone = data['phone']

            user.save()

            Customer = apps.get_model('bank', 'Customer')
            customer = Customer.objects.create(user=user)
            customer.dwolla_id = id

            customer.save()

            # Post save operations, send email e.t.c
            user.signup()

        return None


class SignupStep1Serializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data, *args, **kwargs):
        return User.objects.create_user(**validated_data)


class SignupStep2Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']


class SignupStep3Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['address1', 'city', 'state', 'postal_code']


class SignupStep4Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['ssn', 'date_of_birth']


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
    # dwolla_customer = serializers.SerializerMethodField()
    signup_steps = serializers.SerializerMethodField()
    profile_image_url = serializers.SerializerMethodField()
    funding_sources_user = FundingSourceSerializer(required=False, many=True)
    user_calculations = serializers.SerializerMethodField()
    registration_step = serializers.ReadOnlyField(
        source='get_registation_step')

    class Meta:
        model = User
        fields = (
            'id',
            'guid',
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
            'phone',
            # 'dwolla_customer',
            'is_profile_completed',
            'minimum_transfer_amount',
            'signup_steps',
            'is_even_roundup',
            'is_closed_account',
            'total_debt',
            'profile_image_url',
            'type',
            'dwolla_verified_url',
            'funding_sources_user',
            'user_calculations',
            'registration_step'
        )
        read_only_fields = (
            'id',
            'guid',
            'email',
            'encrypted_id',
            'is_confirmed',
            'signup_steps',
            'is_confirmed',
            'is_closed_account',
            'dwolla_verified_url',
        )

    # def get_dwolla_customer(self, obj):
    #     if hasattr(obj, 'customer'):
    #         return CustomerSerializer(obj.customer).data
    #     return None

    def get_user_calculations(self, obj):
        TransferCalculation = apps.get_model('finance', 'TransferCalculation')

        return TransferCalculationSerializer(
            TransferCalculation.objects.filter(user=obj), many=True).data

    def get_signup_steps(self, obj):
        return obj.signup_steps()

    def get_profile_image_url(self, obj):
        if obj.profile_image:
            return '{}{}'.format(
                settings.BACKEND_URL, obj.profile_image.url)
        return None


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'minimum_transfer_amount',
            'is_even_roundup'
        )


class InviteParentSerilizer(serializers.Serializer):
    email = serializers.EmailField()
