import logging
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import web.serializers as sers
from web.models import User

logger = logging.getLogger('app')


def error404(request):
    return render(request, 'web/html/404.html', status=404)


def error500(request):
    return render(request, 'web/html/500.html', status=500)


def r400(error_message):
    return Response({
        'non_field_errors': [error_message]}, status=400)


class AuthMixin:
    permission_classes = (IsAuthenticated,)


def home(request):
    ctx = {}
    return render(request, 'web/home.html', ctx)


class AuthFacebook(APIView):
    def post(self, request, **kwargs):
        serializer = sers.FacebookAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        try:
            user = User.objects.get(fb_id=d['id'])
        except User.DoesNotExist:
            user = User.create_facebook_user(d)
        return Response({'token': user.get_token().key})


class Login(APIView):
    def post(self, request, **kwargs):
        serializer = sers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        d = serializer.data
        user = User.objects.get(email=d['email'])
        data = {'token': user.get_token().key}

        user.last_access_date = timezone.now()
        user.save()
        return Response(data, status=200)


class PasswordResetRequire(APIView):
    def post(self, request, **kwargs):
        """
        Should return 204 if email doesn't exist.
        Do not allow to check registered people.
        """
        serializer = sers.PasswordResetRequireSerializer(data=request.data)
        if serializer.is_valid():
            d = serializer.data
            user = User.objects.get(email=d['email'])
            user.reset_require()
            return Response({}, status=204)
        return Response({}, status=204)


class PasswordReset(APIView):
    def post(self, request, **kwargs):
        serializer = sers.PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.data
        user = User.objects.get(encrypted_id=d['encrypted_id'])
        user.reset_password(d['new_password'])
        return Response({}, status=204)


class Signup(APIView):
    def post(self, request, **kwargs):
        serializer = sers.SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({}, status=204)


class SignupConfirm(APIView):
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
    Settings for auth users.
    """
    def get(self, request, **kwargs):
        d = {}
        return Response(d, status=200)


class SettingsLogin(APIView):
    """
    Social settings for login page.
    """
    def get(self, request, **kwargs):
        d = {}
        d['facebook_login_url'] = User.get_facebook_login_url()
        return Response(d, status=200)


class UserDetail(AuthMixin, APIView):
    def get(self, request, **kwargs):
        s = sers.UserSerializer(self.request.user)
        return Response(s.data)

    def put(self, request, **kwargs):
        s = sers.UserSerializer(self.request.user, data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
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


class UserChangePassword(AuthMixin, APIView):
    message = 'Your password has been changed!'

    def post(self, request, **kwargs):
        serializer = sers.ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': self.message})


class UserChangeEmail(AuthMixin, APIView):
    message = (
        'Email with confirmation link has been sent to {}! '
        'The link will expire in an 1 hour.'
    )

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
