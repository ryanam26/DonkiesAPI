import logging
import bank.serializers as sers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from web.views import AuthMixin, r400
from bank.models import FundingSource
from finance.models import Account


logger = logging.getLogger('app')


class CustomerDetail(AuthMixin, APIView):
    """
    GET - get customer detail.
    POST - create customer.
    """
    serializer_class = sers.CustomerSerializer

    def post(self, request, **kwargs):
        s = sers.CustomerSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        c = s.save(user=request.user)
        s = sers.CustomerSerializer(c)
        return Response(s.data, status=201)


class FundingSources(AuthMixin, generics.ListCreateAPIView):
    serializer_class = sers.FundingSourceSerializer

    def get_queryset(self):
        return FundingSource.objects.filter(
            account__member__user=self.request.user)

    def post(self, request, **kwargs):
        d = request.data
        account_id = d.pop('account_id', None)
        if not account_id:
            return r400('Please provide account id.')

        try:
            account = Account.objects.get(
                id=account_id, member__user=self.request.user)
        except Account.DoesNotExist:
            return r400('Incorrect account.')

        s = sers.FundingSourceCreateSerializer(data=d)
        s.is_valid(raise_exception=True)
        fs = s.save(account=account)
        s = sers.FundingSourceSerializer(fs)
        return Response(s.data, status=201)
