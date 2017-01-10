import logging
from django.http import Http404
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, ListCreateAPIView)
from rest_framework.response import Response
from rest_framework.views import APIView

import finance.serializers as sers
from web.views import AuthMixin, r400
from finance import tasks
from finance.models import (
    Account, Credentials, Institution, LinkDebt, Member, Transaction)


logger = logging.getLogger('app')


class Accounts(AuthMixin, ListAPIView):
    serializer_class = sers.AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(
            member__user=self.request.user)


class CredentialsListByCode(AuthMixin, ListAPIView):
    serializer_class = sers.CredentialsSerializer

    def get_queryset(self):
        return Credentials.objects.filter(
            institution__code=self.kwargs['institution_code'])


class CredentialsListById(AuthMixin, ListAPIView):
    serializer_class = sers.CredentialsSerializer

    def get_queryset(self):
        return Credentials.objects.filter(
            institution__id=self.kwargs['institution_id'])


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
        return Member.objects.filter(user=self.request.user)

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


class MemberDetail(AuthMixin, RetrieveAPIView):
    serializer_class = sers.MemberSerializer
    lookup_field = 'identifier'

    def get_queryset(self):
        return Member.objects.filter(user=self.request.user)


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

        s = sers.MemberResumeSerializer(
            data=request.data, context={'member': m})
        s.is_valid(raise_exception=True)

        Member.objects.resume_member(
            m.guid, challenges=s.data['challenges'])

        # Call celery task, that should update member's status
        tasks.get_member.delay(m.id)

        return Response(status=204)


class Transactions(AuthMixin, ListAPIView):
    serializer_class = sers.TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(
            account__member__user=self.request.user)
