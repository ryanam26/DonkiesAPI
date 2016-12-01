import logging
from rest_framework.response import Response
from rest_framework.views import APIView

import bank.serializers as sers
from web.views import AuthMixin, r400
from bank.models import Customer


logger = logging.getLogger('app')


class CustomerDetail(AuthMixin, APIView):
    """
    GET - get customer detail.
    POST - create customer.
    """
    serializer_class = sers.CustomerSerializer

    def post(self, request, **kwargs):
        s = sers.CustomerSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save(user=request.user)
        return Response(s.data, status=201)
