from rest_framework import viewsets
from donkiesoauth2.models import DonkiesUser
from django.http import JsonResponse


class DjangoUserViewSet(viewsets.ModelViewSet):
    queryset = DonkiesUser.objects.all()
    serializer_class = DonkiesUser


def api_auth_success(request):
    user = request.user
    if user.is_authenticated():
        try:
            access_token = user.accesstoken_set.get().token
            expires = user.accesstoken_set.get().expires
            refresh_token = user.refreshtoken_set.get().token
        except DonkiesUser.DoesNotExist:
            return JsonResponse({'error': 'not authorized to access api'})

        return JsonResponse({'access_token': access_token,
                             'expires': expires,
                             'refresh_token': refresh_token})
    else:
        return JsonResponse({'error': 'not logged in'})
