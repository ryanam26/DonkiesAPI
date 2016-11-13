import logging
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

import finance.serializers as sers
from web.views import AuthMixin, r400
from finance.models import Member, Account, Credentials, Transaction


logger = logging.getLogger('app')


class Accounts(AuthMixin, ListAPIView):
    serializer_class = sers.AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(
            member__user=self.request.user)


class CredentialsList(AuthMixin, ListAPIView):
    serializer_class = sers.CredentialsSerializer
    queryset = Credentials.objects.all()

    def get_queryset(self):
        return Credentials.objects.filter(
            institution__code=self.kwargs['institution__code'])


class Members(AuthMixin, ListAPIView):
    serializer_class = sers.MemberSerializer

    def get_queryset(self):
        return Member.objects.filter(user=self.request.user)

    def post(self, request, **kwargs):
        s = sers.MemberCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save(user=request.user)
        return Response(s.data, status=201)


class MemberDetail(AuthMixin, RetrieveAPIView):
    serializer_class = sers.MemberSerializer
    lookup_field = 'identifier'

    def get_queryset(self):
        return Member.objects.filter(user=self.request.user)


class Transactions(AuthMixin, ListAPIView):
    serializer_class = sers.TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            account__member__user=self.request.user)
