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
    Transaction, TransferPrepare)
import finance.swagger_serializer as swag_sers
from django.conf import settings
import dwollav2

logger = logging.getLogger('app')


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
    client = dwollav2.Client(id=settings.DWOLLA_ID_DEV,
                             secret=settings.DWOLLA_SECRET_DEV,
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


class Items(AuthMixin, ListCreateAPIView):
    serializer_class = sers.ItemPostSerializer
    # swag_sers.ItemSwaggerSerializer
    # sers.ItemSerializer

    def get(self, request, **kwargs):
        return Response(
            sers.ItemSerializer(
                Item.objects.filter(user=self.request.user),
                many=True
            ).data,
            status=200
        )

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)

    def post(self, request, **kwargs):
        """
        Initially Item is created in Plaid by Plaid Link.
        Plaid Link returns public_token.
        Using this token fetch Item and Accounts from Plaid
        and create them in database.
        """

        if settings.DONKIES_MODE == 'production':
            if request.user.dwolla_verified_url is None:
                missed_fields = create_verified_customer(request.user)
        if missed_fields:
            return Response({'missed params': missed_fields}, status=400)

        if not sers.ItemPostSerializer(data=request.data).is_valid():
            return r400('Missing param.')

        item = Item.objects.create_item_by_data(request.user, request.data)


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
