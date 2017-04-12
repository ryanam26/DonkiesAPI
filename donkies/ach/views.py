import ach.serializers as sers
from rest_framework import generics
from web.views import AuthMixin
from ach.models import TransferStripe, TransferUser, TransferDebt


class TransfersDebt(AuthMixin, generics.ListAPIView):
    serializer_class = sers.TransferDebtSerializer

    def get_queryset(self):
        return TransferDebt.objects.filter(
            account__item__user=self.request.user)


class TransfersStripe(AuthMixin, generics.ListAPIView):
    serializer_class = sers.TransferStripeSerializer

    def get_queryset(self):
        return TransferStripe.objects.filter(
            account__item__user=self.request.user, paid=True)


class TransfersUser(AuthMixin, generics.ListAPIView):
    serializer_class = sers.TransferUserSerializer

    def get_queryset(self):
        return TransferUser.objects.filter(user=self.request.user)
