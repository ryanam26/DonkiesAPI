from rest_framework import viewsets
from donkiesapp.models import LinkedBankAccount
from donkiesapp.serlializers import LinkedBankAccountSerializer


class DjangoUserViewSet(viewsets.ModelViewSet):

    serializer_class = LinkedBankAccountSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return LinkedBankAccount.objects.all()
        return LinkedBankAccount.objects.filter(user=self.request.user)
