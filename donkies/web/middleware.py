from django.contrib.auth import logout
from django.http import HttpResponse
from web.models.authentication_events import AuthenticationEvent
from web.models import User
from django.contrib import auth


class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)

        response = self.get_response(request)
        return response


class AccessControlMiddleware:
    """
    Should be first middleware.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse()
            self.add_headers(response)
            return response

        response = self.get_response(request)
        self.add_headers(response)
        return response

    def add_headers(self, response):
        """
        Adds headers to response.
        """
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Headers'] = (
            'Authorization, Origin, X-Requested-With, Content-Type, Accept')
        response['Access-Control-Allow-Methods'] = (
            'GET, PUT, POST, DELETE, PATCH, OPTIONS')


class CaptureAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = auth.authenticate(
            email=request.POST.get('email'), password=request.POST.get('password'))
        auth_event = AuthenticationEvent()
        auth_event.ip_address = \
            request.META.get('REMOTE_ADDR', '')\
            or request.META.get('HTTP_X_FORWARDED_FOR', '')
        auth_event.is_success = False if user is None else True
        auth_event.save()
        return self.get_response(request)
