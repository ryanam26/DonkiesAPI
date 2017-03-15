import logging
from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, RetrieveDestroyAPIView, ListCreateAPIView)
from rest_framework.response import Response
from rest_framework.views import APIView

import finance.serializers as sers
from web.views import AuthMixin, r400
from finance import tasks
from finance.services.atrium_api import AtriumApi
from finance.models import (
    Account, Credentials, Institution, LinkDebt, Member, Stat,
    Transaction, TransferPrepare, TransferDonkies,
    TransferUser, TransferDebt)

logger = logging.getLogger('app')


class Accounts(AuthMixin, ListAPIView):
    serializer_class = sers.AccountSerializer

    def get_queryset(self):
        """
        All accounts including not active.
        """
        return Account.objects.filter(
            member__user=self.request.user)


class AccountDetail(AuthMixin, RetrieveDestroyAPIView):
    serializer_class = sers.AccountSerializer

    def get_queryset(self):
        return Account.objects.active().filter(
            member__user=self.request.user)


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
            member__user=self.request.user,
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
            id=id, member__user=request.user)
        is_active = request.data.get('is_active', None)
        if is_active is None:
            return r400('Missing param.')

        if is_active is False:
            member = account.member
            if member.accounts.filter(is_active=True).count() <= 1:
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
            id=kwargs['pk'], member__user=request.user)

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
            id=id, member__user=request.user)
        Account.objects.set_funding_source(account.id)
        return Response(status=201)


class CredentialsListByCode(AuthMixin, ListAPIView):
    """
    Credentials from database. (Old implementation)
    """
    serializer_class = sers.CredentialsSerializer

    def get_queryset(self):
        return Credentials.objects.filter(
            institution__code=self.kwargs['institution_code'])


class CredentialsListById(AuthMixin, ListAPIView):
    """
    Credentials from database. (Old implementation)
    """
    serializer_class = sers.CredentialsSerializer

    def get_queryset(self):
        return Credentials.objects.filter(
            institution__id=self.kwargs['institution_id'])


class CredentialsLiveListByCode(AuthMixin, APIView):
    """
    Credentials directly from Atrium.
    """
    def get(self, request, **kwargs):
        i = Institution.objects.get(code=self.kwargs['institution_code'])
        a = AtriumApi()
        return Response(a.get_credentials(i.code))


class CredentialsLiveListById(AuthMixin, APIView):
    """
    Credentials directly from Atrium.
    """
    def get(self, request, **kwargs):
        i = Institution.objects.get(id=self.kwargs['institution_id'])
        a = AtriumApi()
        return Response(a.get_credentials(i.code))


class InstitutionsSuggest(AuthMixin, APIView):
    """
    Returns data for React InputAutocompleteAsync.
    In "GET" params receives "value" for filtering.
    """
    def get(self, request, **kwargs):
        value = request.query_params.get('value', None)
        if value is None:
            return Response([])

        l = []
        qs = Institution.objects.filter(name__icontains=value)
        for i in qs:
            l.append({'value': i.name, 'id': i.id})
        return Response(l)


class Institutions(AuthMixin, ListAPIView):
    serializer_class = sers.InstitutionSerializer
    queryset = Institution.objects.all()


class InstitutionDetail(AuthMixin, RetrieveAPIView):
    serializer_class = sers.InstitutionSerializer
    queryset = Institution.objects.all()


class LinkDebts(AuthMixin, ListCreateAPIView):
    serializer_class = sers.LinkDebtSerializer

    def get_queryset(self):
        return LinkDebt.objects.filter(user=self.request.user)

    def post(self, request, **kwargs):
        d = request.data
        try:
            Account.objects.get(
                member__user=self.request.user, id=d['account'])
        except Account.DoesNotExist:
            r400('Incorrect account.')

        s = sers.LinkDebtCreateSerializer(data=d)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data, status=201)


class Members(AuthMixin, ListAPIView):
    serializer_class = sers.MemberSerializer

    def get_queryset(self):
        return Member.objects.active().filter(user=self.request.user)

    def post(self, request, **kwargs):
        s = sers.MemberCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        member = s.save(user=request.user)
        s = sers.MemberSerializer(member)

        # Call celery task, that will call Atrium API
        # until get finished status and save updated member
        # to database
        tasks.get_member.delay(member.id)

        return Response(s.data, status=201)


class MemberDetail(AuthMixin, RetrieveDestroyAPIView):
    serializer_class = sers.MemberSerializer
    lookup_field = 'identifier'

    def get_queryset(self):
        return Member.objects.active().filter(user=self.request.user)

    def perform_destroy(self, instance):
        Member.objects.delete_member(instance.id)


class MemberResume(AuthMixin, APIView):
    """
    Used when member has challenges.
    """
    def post(self, request, identifier, **kwargs):
        try:
            m = Member.objects.get(
                user=self.request.user, identifier=identifier)
        except Member.DoesNotExist:
            raise Http404()

        s = sers.MemberResumeSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        Member.objects.resume_member(
            m.guid, challenges=s.data['challenges'])

        m.status = Member.REQUESTED
        m.save()

        # Call celery task, that should update member's status
        tasks.get_member.delay(m.id)

        return Response(status=204)


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
            account__member__user=self.request.user)


class TransfersDebt(AuthMixin, ListAPIView):
    serializer_class = sers.TransferDebtSerializer

    def get_queryset(self):
        return TransferDebt.objects.filter(
            account__member__user=self.request.user)


class TransfersDonkies(AuthMixin, ListAPIView):
    serializer_class = sers.TransferDonkiesSerializer

    def get_queryset(self):
        return TransferDonkies.objects.filter(
            account__member__user=self.request.user, is_sent=True)


class TransfersPrepare(AuthMixin, ListAPIView):
    serializer_class = sers.TransferPrepareSerializer

    def get_queryset(self):
        return TransferPrepare.objects.filter(
            account__member__user=self.request.user)


class TransfersUser(AuthMixin, ListAPIView):
    serializer_class = sers.TransferUserSerializer

    def get_queryset(self):
        return TransferUser.objects.filter(user=self.request.user)
