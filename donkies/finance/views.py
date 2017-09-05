import datetime
import logging
import finance.serializers as sers
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, RetrieveDestroyAPIView, ListCreateAPIView)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from finance.tasks import (
    process_plaid_webhooks, fetch_transactions, fetch_history_transactions,
    fetch_account_numbers)
from web.views import AuthMixin, r400
from finance.models import (
    Account, FetchTransactions, Institution, Item, Lender, Stat,
    Transaction, TransferPrepare, TransferCalculation)
import finance.swagger_serializer as swag_sers
from finance.services.plaid_api import PlaidApi
from finance.services.dwolla_api import DwollaAPI
from web.formatResponse import format_response
from finance.models.transfer_calculation import charge_application
from decimal import *


logger = logging.getLogger('app')


def fetch_account_numbers_view(request, account_id):
    """
    Admin view.
    Run task to fetch account_number and routing_number.
    """
    fetch_account_numbers.delay(account_id)
    msg = 'Request to Plaid sent. Please check result few seconds later.'
    messages.success(request, msg)
    return HttpResponseRedirect('/admin/finance/account/')


class Accounts(AuthMixin, GenericAPIView):
    serializer_class = sers.CreateMultipleAccountSerializer
    queryset = Account.objects.all()

    def get(self, request, **kwargs):
        """
        All accounts including not active.
        """
        return Response(
            sers.AccountSerializer(
                Account.objects.filter(item__user=self.request.user),
                many=True
            ).data
        )

    def post(self, request, **kwargs):
        """
        Creating only manual accounts<br/>
        (for debt accounts).<br/>
        All accounts that are in Plaid come from Item<br/>
        and do not created by API.<br/>

        Accounts come in array.<br/>
        Creates multiple accounts.<br/>

        Example request:
        <pre>
        {
            "accounts": [
                {
                    "institution_id": <b>int</b>
                    "account_number": <b>string</b>
                    "additional_info": <b>string</b>
                }
            ]
        }
        </pre>

        """
        l = request.data.get('accounts')

        for data in l:
            s = sers.CreateAccountSerializer(data=data)
            s.is_valid(raise_exception=True)
            s.save(user=request.user)

        return Response(
            status=201
        )


class AccountDetail(AuthMixin, RetrieveDestroyAPIView):
    """
    get:
        Return Account by id
    delete:
        Not implement yet
    """
    serializer_class = sers.AccountSerializer

    def get_queryset(self):
        return Account.objects.active().filter(
            item__user=self.request.user)


class AccountsEditShare(AuthMixin, GenericAPIView):
    serializer_class = sers.AccountsEditShareSerializer

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
        """
        <b>Edit transfer_share for debt accounts.</b>

        Example request:
        <pre>
        {
            id7: 35,
            id8: 65
        }
        </pre>
        <ol>
            <li>The ids should be equal to ids in database.</li>
            <li>The total sum of share should be equal to 100.</li>
        </ol>

        Returns 200 or 400, no error messages.<br/>
        Frontend checks everything before sending data.

        """

        l = self.get_list(request.data)
        if not self.validate_ids(l):
            return Response(status=400)

        if not self.validate_sum(l):
            return Response(status=400)

        self.update(l)
        return Response()


class AccountsSetActive(AuthMixin, GenericAPIView):
    """
    Activate / Deactivate account.<br/>
    1) Can not deactivate account if Item has only 1 active account.<br/>
    2) Can not deactivate funding source.
    """
    serializer_class = sers.AccountsSetActiveSerializer

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


class AccountsSetNumber(AuthMixin, ListAPIView):
    """
    get:
        Not implement yet!!
    """
    serializer_class = swag_sers.AccountsSetNumberSwaggerSerializer

    def post(self, request, **kwargs):
        """
        Set account_number.
        ---
        response_serializer: AccountSerializer
        parameters:
            - name: account_number
              pytype: AccountSerializer
        """
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


class AccountsSetPrimary(AuthMixin, APIView):
    """
    Set primary account.
    """

    def post(self, request, **kwargs):
        id = kwargs['pk']
        account = Account.objects.get(
            id=id, item__user=request.user)
        Account.objects.set_primary(account.id)
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
        qs = Institution.objects.filter(name__icontains=value, is_active=True)
        qs = qs.exclude(id__in=ids)

        for i in qs:
            l.append({'value': i.name, 'id': i.id})

        return Response(l)


class Institutions(AuthMixin, ListAPIView):
    serializer_class = sers.InstitutionSerializer
    queryset = Institution.objects.filter(is_active=True)


class DebtInstitutions(AuthMixin, ListAPIView):
    """
    Manual institutions.
    """
    serializer_class = sers.InstitutionSerializer
    queryset = Institution.objects.filter(is_manual=True, is_active=True)


class InstitutionDetail(AuthMixin, RetrieveAPIView):
    serializer_class = sers.InstitutionSerializer
    queryset = Institution.objects.filter(is_active=True)


class CreateTransaction(AuthMixin, GenericAPIView):
    serializer_class = sers.CreateTransactionSerializer

    def post(self, request, **kwargs):
        access_token = request.data['access_token']
        Transaction.objects.create_or_update_transactions(access_token)
        Transaction.objects.filter(account__item__user=request.user)
        return Response(
            sers.TransferPrepareSerializer(
                Transaction.objects.filter(account__item__user=request.user),
                many=True
            ).data,
            status=200
        )


class MakeTransfer(AuthMixin, ListCreateAPIView):
    """
    This endpoint only for testing
    """
    serializer_class = sers.MakeTransferSerializer

    def get_queryset(self):
        return Response(status=200)

    def post(self, request, **kwargs):
        """
        Transfer amount to user dwolla account
        """
        amount = Decimal(request.data['amount'])
        transfer = charge_application(amount, request.user)
        return Response(transfer, status=200)


class Items(AuthMixin, ListCreateAPIView):
    serializer_class = sers.ItemPostSerializer

    def get_queryset(self):

        return Response(
            sers.ItemSerializer(
                Item.objects.filter(user=self.request.user), many=True
            ).data, status=200
        )

    def get(self, request, **kwargs):

        return Response(
            sers.ItemSerializer(
                Item.objects.filter(user=self.request.user), many=True
            ).data, status=200
        )

    def post(self, request, **kwargs):
        """
        Initially Item is created in Plaid by Plaid Link.
        Plaid Link returns public_token.
        Using this token and account_id fetch Item and Accounts from Plaid
        and create them in database.
        """
        if not sers.ItemPostSerializer(data=request.data).is_valid():
            return r400('Missing param.')

        try:
            item = Item.objects.create_item_by_data(request.user, request.data)
        except Exception as e:
            if hasattr(e, 'body'):
                return Response(e.body, e.status)
            return Response(format_response(e.args, 400), 400)

        # Fill FetchTransactions (history model)
        FetchTransactions.objects.create_all(item)

        # Get accounts
        try:
            Account.objects.create_or_update_accounts(
                item, request.user, item.access_token
            )
        except Exception as e:
            return Response(e.body, e.status)
        # request.data['account_id']
        # Fetch recent transactions
        fetch_transactions.delay(item.access_token)

        # Fetch history transactions
        fetch_history_transactions.apply_async(countdown=60)

        s = sers.ItemSerializer(item)

        return Response(s.data, status=201)


class PauseItems(AuthMixin, ListCreateAPIView):
    serializer_class = sers.PauseItemsSerializer

    def get_queryset(self):
        return Response(
            sers.ItemSerializer(
                Item.objects.filter(user=self.request.user),
                many=True
            ).data,
            status=200
        )

    def get(self, request, **kwargs):
        return Response(
            sers.ItemSerializer(
                Item.objects.filter(user=request.user),
                many=True
            ).data,
            status=200
        )

    def post(self, request, **kwargs):
        item_id = request.data['item_id']
        pause = request.data['pause']
        item = Item.objects.get(id=item_id, user=request.user)

        if pause:
            item.pause_on()

        if not pause:
            item.pause_off()

        return Response(
            sers.ItemSerializer(
                Item.objects.filter(user=self.request.user),
                many=True
            ).data,
            status=200
        )


class FakeRoundups(AuthMixin, GenericAPIView):
    serializer_class = sers.FakeRoundupsSerilizer

    def post(self, request, **kwargs):
        """
        This endpoint only for testing <br/>
        Imitate situation if user reached $5 and system make transfer
        to coinstash

        parameters:
            - roundup: roundup_amount
        """
        tr_calc = TransferCalculation.objects.filter(user=request.user).first()
        roundup = round(Decimal(request.data['roundup']), 2)
        tr_calc.calculate_roundups(roundup)

        return Response(
            TransferCalculation.objects.values().get(id=tr_calc.id),
            status=200
        )


class SetMinimumValueForTransfer(AuthMixin, GenericAPIView):
    serializer_class = sers.SetMinValueSerializer

    def post(self, request, **kwargs):
        transfer_calc, created = TransferCalculation.objects.get_or_create(
            user=request.user
        )
        transfer_calc.min_amount = request.data['min_value']
        transfer_calc.save()

        serializer = sers.TransferCalculationSerializer(transfer_calc)
        return Response(serializer.data, status=200)


class ItemDetail(AuthMixin, RetrieveDestroyAPIView):
    serializer_class = sers.ItemSerializer
    lookup_field = 'guid'

    def get_queryset(self):
        return Item.objects.active().filter(user=self.request.user)

    def perform_destroy(self, instance):
        Item.objects.delete_item(instance.id)


class Lenders(AuthMixin, ListCreateAPIView):
    serializer_class = sers.InstitutionSerializer

    def get_queryset(self):
        ids = Lender.objects.filter(
            user=self.request.user).values_list('institution_id', flat=True)
        return Institution.objects.filter(id__in=ids)

    def post(self, request, **kwargs):
        institution_id = request.data.get('institution_id')
        account_number = request.data.get('account_number')
        institution = Institution.objects.get(id=institution_id)
        Lender.objects.create_lender(
            request.user, institution, account_number)
        return Response(status=201)


class LenderDetail(AuthMixin, APIView):
    def delete(self, request, **kwargs):
        id = kwargs['id']
        Lender.objects.filter(user=request.user, institution_id=id).delete()
        return Response(status=204)


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
