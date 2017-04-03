import logging
import bank.serializers as sers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from web.views import AuthMixin, r400
from bank.services.dwolla_api import DwollaApi
from bank.models import FundingSource
from finance.models import Account


logger = logging.getLogger('app')


class CreateFundingSourceByIAV(AuthMixin, APIView):
    """
    At first frontend creates funding source in Dwolla.
    Then it sends account_id and dwolla_id to API
    to save funding source in database.
    """
    def post(self, request, **kwargs):
        account_id = request.data.pop('account_id')
        dwolla_id = request.data.pop('dwolla_id')

        fs = FundingSource.objects.create_funding_source_iav(
            account_id, dwolla_id)
        s = sers.FundingSourceSerializer(fs)
        return Response(s.data, status=201)


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
            account__item__user=self.request.user)

    def post(self, request, **kwargs):
        """
        Create funding source manually by
        account_number and routing number.
        """
        d = request.data
        account_id = d.pop('account_id', None)
        if not account_id:
            return r400('Please provide account id.')

        try:
            account = Account.objects.get(
                id=account_id, item__user=self.request.user)
        except Account.DoesNotExist:
            return r400('Incorrect account.')

        s = sers.FundingSourceCreateSerializer(data=d)
        s.is_valid(raise_exception=True)
        fs = s.save(account=account)
        s = sers.FundingSourceSerializer(fs)
        return Response(s.data, status=201)


class GetIAVToken(AuthMixin, APIView):
    def post(self, request, **kwargs):
        customer_id = kwargs['dwolla_customer_id']
        d = DwollaApi()
        token = d.get_iav_token(customer_id)
        if token is None:
            return Response({'message': 'Server error.'}, status=400)
        return Response({'token': token})
