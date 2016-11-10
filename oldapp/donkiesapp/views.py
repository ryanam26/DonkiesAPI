from django.shortcuts import render_to_response
from django.template.context import RequestContext

from rest_framework import viewsets
# from donkiesapp.models import LinkedBankAccount
# from donkiesapp.serlializers import LinkedBankAccountSerializer


# class DjangoUserViewSet(viewsets.ModelViewSet):
#
#     serializer_class = LinkedBankAccountSerializer
#
#     def get_queryset(self):
#         if self.request.user.is_superuser:
#             return LinkedBankAccount.objects.all()
#         return LinkedBankAccount.objects.filter(user=self.request.user)


def login(request):
    context = RequestContext(request, {'request': request, 'user': request.user, 'next': request.GET.get('next')})
    return render_to_response('login.html', context=context)