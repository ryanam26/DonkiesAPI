import logging
from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, RetrieveDestroyAPIView, ListCreateAPIView)
from rest_framework.response import Response
from rest_framework.views import APIView

import finance.serializers as sers
from web.views import AuthMixin, r400
from finance.models import (
    Account, Institution, Item, Stat, Transaction,
    TransferPrepare, TransferDonkies, TransferUser, TransferDebt)

logger = logging.getLogger('app')


class Accounts(AuthMixin, ListAPIView):
    serializer_class = sers.AccountSerializer

    def get_queryset(self):
        """
        All accounts including not active.
        """
        return Account.objects.filter(
            item__user=self.request.user)


class AccountDetail(AuthMixin, RetrieveDestroyAPIView):
    serializer_class = sers.AccountSerializer

    def get_queryset(self):
        return Account.objects.active().filter(
            item__user=self.request.user)


class AccountsEditShare(AuthMixin, APIView):
    """
    Edit transfer_share for debt accounts.

    Example request: {id7: 35, id8: 65}
    1) The ids should be equal to ids in database.
    2) The total sum of share should be equal to 100.

    Returns 200 or 400, no error messages.
    Frontend checks everything before sending data.
    """
    def get_queryset(self):
        return Account.objects.active().filter(
            item__user=self.request.user,
            type_ds=Account.DEBT)

    def get_list(self, data):
        """
        Converts query dict from request post
        from {id7: 35, id8: 65} to [(7, 35), (8, 65)]
        """
        l = []
        for key, value in data.items():
            if 'id' in key:
                key = key.lstrip('id')
                id = int(key)
                value = int(value)
                l.append((id, value))
        return l

    def validate_ids(self, l):
        qs = self.get_queryset()
        ids1 = list(qs.values_list('id', flat=True))
        ids2 = [tup[0] for tup in l]
        if sorted(ids1) == sorted(ids2):
            return True
        return False

    def validate_sum(self, l):
        ids = [tup[1] for tup in l]
        if sum(ids) == 100:
            return True
        return False

    def update(self, l):
        for id, share in l:
            Account.objects.active().filter(id=id).update(transfer_share=share)

    def put(self, request, **kwargs):
        l = self.get_list(request.data)
        if not self.validate_ids(l):
            return Response(status=400)

        if not self.validate_sum(l):
            return Response(status=400)

        self.update(l)
        return Response()


class AccountsSetActive(AuthMixin, APIView):
    """
    Activate / Deactivate account.
    Can not deactivate account if member has only 1 active account.
    """
    def put(self, request, **kwargs):
        id = kwargs['pk']
        account = Account.objects.get(
            id=id, item__user=request.user)
        is_active = request.data.get('is_active', None)
        if is_active is None:
            return r400('Missing param.')

        if is_active is False:
            item = account.item
            if item.accounts.filter(is_active=True).count() <= 1:
                msg = (
                    'You can not deactivate account. '
                    'You should have at least one active account '
                    'at financial institution'
                )
                return r400(msg)

        Account.objects.change_active(account.id, is_active)
        return Response(status=204)


class AccountsSetNumber(AuthMixin, APIView):
    """
    Set account_number.
    """
    def post(self, request, **kwargs):
        account = Account.objects.get(
            id=kwargs['pk'], item__user=request.user)

        account_number = request.data.get('account_number', None)
        if account_number is None:
            return r400('Incorrect request')

        try:
            Account.objects.set_account_number(account.id, account_number)
        except ValidationError as e:
            return r400(e.args[0])
        return Response(status=201)


class AccountsSetFundingSource(AuthMixin, APIView):
    """
    Set funding source for transfer for debit accounts.
    """
    def post(self, request, **kwargs):
        id = kwargs['pk']
        account = Account.objects.get(
            id=id, item__user=request.user)
        Account.objects.set_funding_source(account.id)
        return Response(status=201)


class InstitutionsSuggest(AuthMixin, APIView):
    """
    Returns data for React InputAutocompleteAsync.
    In "GET" params receives "value" for filtering.

    Institutions (members) that user already has should
    be excluded from result.
    """
    def get(self, request, **kwargs):
        value = request.query_params.get('value', None)
        if value is None:
            return Response([])

        # Exisiting user's institutions.
        qs = Item.objects.active()\
            .filter(user=request.user)\
            .values_list('institution_id', flat=True)
        ids = list(qs)

        l = []
        qs = Institution.objects.filter(name__icontains=value)
        qs = qs.exclude(id__in=ids)

        for i in qs:
            l.append({'value': i.name, 'id': i.id})

        return Response(l)


class Institutions(AuthMixin, ListAPIView):
    serializer_class = sers.InstitutionSerializer
    queryset = Institution.objects.all()


class InstitutionDetail(AuthMixin, RetrieveAPIView):
    serializer_class = sers.InstitutionSerializer
    queryset = Institution.objects.all()


class StatView(AuthMixin, APIView):
    def get(self, request, **kwargs):
        return Response(Stat.objects.get_json(self.request.user.id))


class Transactions(AuthMixin, ListAPIView):
    """
    All user's transactions.
    """
    serializer_class = sers.TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.active().filter(
            account__item__user=self.request.user)


class TransfersDebt(AuthMixin, ListAPIView):
    serializer_class = sers.TransferDebtSerializer

    def get_queryset(self):
        return TransferDebt.objects.filter(
            account__item__user=self.request.user)


class TransfersDonkies(AuthMixin, ListAPIView):
    serializer_class = sers.TransferDonkiesSerializer

    def get_queryset(self):
        return TransferDonkies.objects.filter(
            account__item__user=self.request.user, is_sent=True)


class TransfersPrepare(AuthMixin, ListAPIView):
    serializer_class = sers.TransferPrepareSerializer

    def get_queryset(self):
        return TransferPrepare.objects.filter(
            account__item__user=self.request.user)


class TransfersUser(AuthMixin, ListAPIView):
    serializer_class = sers.TransferUserSerializer

    def get_queryset(self):
        return TransferUser.objects.filter(user=self.request.user)
