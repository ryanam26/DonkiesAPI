import logging
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseForbidden
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
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


@api_view(['GET'])
def api_root(request):
    return HttpResponseForbidden()


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


class Login(APIView):
    def post(self, request, **kwargs):
        serializer = sers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        d = serializer.data
        user = User.objects.get(email=d['email'])
        if not user.is_confirmed:
            return r400('Your email is not confirmed.')

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


class OauthTest(AuthMixin, APIView):
    def get(self, request, **kwargs):
        return Response({'hello': request.user.email})


def login(request):
    ctx = {
        'user': request.user,
        'next': request.GET.get('next', '')
    }
    return render(request, 'web/login.html', ctx)


def logout(request):
    auth_logout(request)
    return redirect(reverse('auth_login'))
