import logging
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import web.serializers as sers
from web.models import User
from finance.models import Item
from bank.tasks import create_customer

from rest_framework.permissions import AllowAny
from rest_framework.schemas import SchemaGenerator
from rest_framework_swagger import renderers
from rest_framework.generics import ListAPIView, GenericAPIView
import dwollav2
from django.contrib.auth import logout
from django.apps import apps
from web.services.sparkpost_service import SparkPostService
from django.core.mail import send_mail
import hashlib


def has_missed_fields(request_body):
    """
    Check fields for Dwolla verified customer
    """
    missed_values = []
    for key in request_body:
        if request_body[key] is None:
            missed_values.append(key)

    return missed_values


def create_verified_customer(user):
    """
    Creates Dwolla verified customer
    and plugin to User model
    """
    client = dwollav2.Client(id=settings.DWOLLA_ID_SANDBOX,
                             secret=settings.DWOLLA_SECRET_SANDBOX,
                             environment=settings.PLAID_ENV)
    app_token = client.Auth.client()
    request_body = {'firstName': user.first_name,
                    'lastName': user.last_name,
                    'email': user.email,
                    'type': user.type,
                    'address1': user.address1,
                    'city': user.city,
                    'state': user.state,
                    'postalCode': user.postal_code,
                    'dateOfBirth': str(user.date_of_birth),
                    'ssn': user.ssn}
    missed_fields = has_missed_fields(request_body)
    if missed_fields:
        return missed_fields
    customer = app_token.post('customers', request_body)
    user.dwolla_verified_url = customer.headers['location']
    user.save()

    return missed_fields


class SwaggerSchemaView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer
    ]

    def get(self, request):
        generator = SchemaGenerator()
        schema = generator.get_schema(request=request)

        return Response(schema)


logger = logging.getLogger('app')


def error404(request):
    return render(request, 'web/html/404.html', status=404)


def error500(request):
    return render(request, 'web/html/500.html', status=500)


def r400(error_message):
    return Response({
        'non_field_errors': [error_message]}, status=400)


def clean_plaid(request):
    """
    Admin view. Used for debug production.
    Clean all Plaid items.
    """
    Item.objects.clean_plaid()
    messages.success(request, 'Plaid has been cleaned.')
    return HttpResponseRedirect('/admin/web/user/')


class AuthMixin:
    permission_classes = (IsAuthenticated,)


def home(request):
    return HttpResponse('API')


class AuthFacebook(GenericAPIView):
    serializer_class = sers.FacebookAuthSerializer

    def post(self, request, **kwargs):
        serializer = sers.FacebookAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        try:
            user = User.objects.get(
                Q(fb_id=d['id']) | Q(email=d['email']))
        except User.DoesNotExist:
            user = User.create_facebook_user(d)

        return Response({'token': user.get_token().key})


class Login(GenericAPIView):
    serializer_class = sers.LoginSerializer

    def post(self, request, **kwargs):
        serializer = sers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        d = serializer.data
        user = User.objects.get(email=d['email'])
        data = {'token': user.get_token().key}

        user.last_access_date = timezone.now()
        user.save()
        return Response(data, status=200)


class Logout(APIView):

    def get(self, request, **kwargs):
        """
        Logout endpoint
        """
        Token = apps.get_model('web', 'Token')
        tokens = Token.objects.filter(user=request.user)
        for token in tokens:
            token.delete()
        logout(request)
        return Response({"message": "logout success"}, status=200)


class PasswordResetRequest(GenericAPIView):
    serializer_class = sers.PasswordResetRequestSerializer

    def post(self, request, **kwargs):
        serializer = sers.PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.data
        user = User.objects.get(email=d['email'])
        user.reset_request()
        return Response({}, status=204)


class PasswordReset(GenericAPIView):
    serializer_class = sers.PasswordResetSerializer

    def post(self, request, **kwargs):
        serializer = sers.PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.data
        user = User.objects.get(encrypted_id=d['encrypted_id'])
        user.reset_password(d['new_password'])
        return Response({}, status=204)


class Signup(GenericAPIView):
    serializer_class = sers.SignupSerializer

    def post(self, request, **kwargs):
        serializer = sers.SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
        except Exception as e:
            res = e.args[0].args[0].body['_embedded']
            return Response(res, status=403)
        user = User.objects.get(email=request.data.get('email', None))

        return Response({
            'token': user.get_token().key
        }, status=201)


class SignupParent(GenericAPIView):
    serializer_class = sers.SignupParentSerializer

    def post(self, request, **kwargs):
        serializer = sers.SignupParentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Token = apps.get_model('web', 'Token')

        try:
            serializer.save()
        except Exception as e:
            return Response({'email_child': [e.args[0]], 'status': 400}, status=400)
        user = User.objects.get(email=request.data['email'])
        token = Token.objects.get(user=user)

        return Response({'token': token.key}, status=201)


class SignupConfirm(GenericAPIView):
    serializer_class = sers.SignupConfirmSerializer

    def post(self, request, **kwargs):
        serializer = sers.SignupConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.data
        user = User.objects.get(encrypted_id=d['encrypted_id'])

        token = user.signup_confirm()
        data = {'token': token.key}
        return Response(data, status=201)


class Settings(AuthMixin, APIView):
    """
    Global settings for auth users.
    """

    def get(self, request, **kwargs):
        d = {
            'transfer_amounts': [t[0] for t in User.TRANSFER_AMOUNT_CHOICES],
            'plaid_env': settings.PLAID_ENV,
            'plaid_public_key': settings.PLAID_PUBLIC_KEY,
            'plaid_products': settings.PLAID_LINK_PRODUCTS,
            'plaid_client_name': settings.PLAID_LINK_CLIENT_NAME,
            'plaid_webhooks_url': settings.PLAID_WEBHOOKS_URL
        }
        return Response(d, status=200)


class SettingsLogin(APIView):
    """
    Social settings for login page.
    """

    def get(self, request, **kwargs):
        d = {}
        d['facebook_login_url'] = User.get_facebook_login_url()
        return Response(d, status=200)


class UserDetail(AuthMixin, GenericAPIView):
    serializer_class = sers.SignupSerializer
    queryset = User.objects.all()

    def get(self, request, **kwargs):
        s = sers.UserSerializer(self.request.user)
        return Response(s.data)

    def put(self, request, **kwargs):
        if request.user.is_profile_completed:
            return r400('Profile is completed and can not be changed.')

        s = sers.UserSerializer(self.request.user, data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        # Create customer after User completed profile
        create_customer.apply_async(args=[request.user.id], countdown=5)
        return Response(s.data)


class UserResendRegConfirmationLink(AuthMixin, APIView):
    def get(self, request, **kwargs):
        u = request.user
        if u.is_confirmed:
            return Response({'message': 'Your account is confirmed.'})

        u.resend_confirmation_link()
        u.save()
        return Response({
            'message': 'Email with confirmation link has been sent.'
        })


class UserChangePassword(AuthMixin, GenericAPIView):
    message = 'Your password has been changed!'
    serializer_class = sers.ChangePasswordSerializer

    def post(self, request, **kwargs):
        serializer = sers.ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': self.message})


class UserChangeEmail(AuthMixin, GenericAPIView):
    message = (
        'Email with confirmation link has been sent to {}! '
        'The link will expire in an 1 hour.'
    )
    serializer_class = sers.ChangeEmailSerializer

    def post(self, request, **kwargs):
        serializer = sers.ChangeEmailSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': self.message.format(request.data['new_email'])})


class UserChangeEmailConfirm(APIView):
    message = 'Your email has been successfully changed!'

    def post(self, request, **kwargs):
        try:
            user = User.objects.get(encrypted_id=kwargs['encrypted_id'])
        except User.DoesNotExist:
            return r400('Incorrect id.')

        if not user.change_email_confirm(kwargs['token']):
            return r400('Incorrect link or expired token.')

        return Response({'message': self.message})


class UserSettings(AuthMixin, generics.UpdateAPIView):
    serializer_class = sers.UserSettingsSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        return User.objects.get(id=self.request.user.id)


class UserCloseAccount(AuthMixin, APIView):
    def post(self, request, **kwargs):
        self.request.user.close_account()
        return Response(status=204)


class InviteParent(AuthMixin, APIView):
    message = 'Your child wants to add you as a parent on Donkies. Please sign up here {}'
    personal_string = 'id-{}_mail-{}'

    def post(self, request, **kwargs):

        if settings.DONKIES_MODE == 'production':
            front_end_url = settings.FRONTEND_URL
        elif settings.DONKIES_MODE == 'development':
            front_end_url = 'http://localhost:8080'

        m = hashlib.md5()
        personal_string = self.personal_string.format(request.user.id, request.user.email)
        m.update(personal_string.encode())

        url = '{}/registration_parent?ref={}&?u={}'.format(
            front_end_url, m.hexdigest(), request.user.id
        )

        message = self.message.format(url)

        return Response({
            'link': url,
        }, status=200)
