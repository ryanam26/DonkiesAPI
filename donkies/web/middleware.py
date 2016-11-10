from django.contrib.auth import logout
from django.http import HttpResponse


class AccessControlMiddleware:
    def process_request(self, request):
        if request.method == 'OPTIONS':
            return HttpResponse()

    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Headers'] = (
            'Authorization, Origin, X-Requested-With, Content-Type, Accept')
        response['Access-Control-Allow-Methods'] = (
            'GET, PUT, POST, DELETE, PATCH, OPTIONS')
        return response


class ActiveUserMiddleware:
    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
