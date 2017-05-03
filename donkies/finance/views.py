import datetime
import logging
import finance.serializers as sers
from django.core.exceptions import ValidationError
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, RetrieveDestroyAPIView, ListCreateAPIView)
from rest_framework.response import Response
from rest_framework.views import APIView
from finance.tasks import (
    process_plaid_webhooks, fetch_transactions, fetch_history_transactions)
from web.views import AuthMixin, r400
from finance.models import (
    Account, FetchTransactions, Institution, Item, Stat, Transaction,
    TransferPrepare)

logger = logging.getLogger('app')


class Accounts(AuthMixin, ListAPIView):
    serializer_class = sers.AccountSerializer

    def get_queryset(self):
        """
        All accounts including not active.
        """
        return Account.objects.filter(
            item__user=self.request.user)

    def post(self, request, **kwargs):
        """
        Creating only manual accounts
        (for debt accounts).
        All accounts that are in Plaid come from Item
        and do not created by API.

        Accounts come in array.
        Creates multiple accounts.
        """
        l = request.data.get('accounts')
        for data in l:
            s = sers.CreateAccountSerializer(data=data)
            s.is_valid(raise_exception=True)
            s.save(user=request.user)
        return Response(status=201)


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
    1) Can not deactivate account if Item has only 1 active account.
    2) Can not deactivate funding source.
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

        if account.is_funding_source_for_transfer:
            msg = 'You can not deactivate funding source account.'
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

    Institutions that user already has should
    be excluded from result.

    Used only for debt manual accounts.
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


class DebtInstitutions(AuthMixin, ListAPIView):
    """
    Manual institutions.
    """
    serializer_class = sers.InstitutionSerializer
    queryset = Institution.objects.filter(is_manual=True)


class InstitutionDetail(AuthMixin, RetrieveAPIView):
    serializer_class = sers.InstitutionSerializer
    queryset = Institution.objects.all()


class Items(AuthMixin, ListCreateAPIView):
    serializer_class = sers.ItemSerializer

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)

    def post(self, request, **kwargs):
        """
        Initially Item is created in Plaid by Plaid Link.
        Plaid Link returns public_token.
        Using this token fetch Item and Accounts from Plaid
        and create them in database.
        """
        public_token = request.data.get('public_token')
        item = Item.objects.create_item_by_public_token(
            request.user, public_token)

        # Fill FetchTransactions (history model)
        FetchTransactions.objects.create_all(item)

        # Get accounts
        Account.objects.create_or_update_accounts(item.access_token)

        # Fetch recent transactions
        fetch_transactions.delay(item.access_token)

        # Fetch history transactions
        fetch_history_transactions.apply_async(countdown=60)

        s = sers.ItemSerializer(item)
        return Response(s.data, status=201)


class ItemDetail(AuthMixin, RetrieveDestroyAPIView):
    serializer_class = sers.ItemSerializer
    lookup_field = 'guid'

    def get_queryset(self):
        return Item.objects.active().filter(user=self.request.user)

    def perform_destroy(self, instance):
        Item.objects.delete_item(instance.id)


class PlaidWebhooks(APIView):
    def post(self, request, **kwargs):
        data = request.data
        process_plaid_webhooks.delay(data)
        return Response(status=204)


class StatView(AuthMixin, APIView):
    def get(self, request, **kwargs):
        return Response(Stat.objects.get_json(self.request.user.id))


class Transactions(AuthMixin, ListAPIView):
    """
    User's transactions for the past month.
    """
    serializer_class = sers.TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.active().filter(
            account__item__user=self.request.user,
            date__gte=datetime.date.today() - datetime.timedelta(days=30)
        )


class TransfersPrepare(AuthMixin, ListAPIView):
    serializer_class = sers.TransferPrepareSerializer

    def get_queryset(self):
        return TransferPrepare.objects.filter(
            account__item__user=self.request.user)
