from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class TokenExpired(APIException):
    status_code = 400
    default_detail = 'Token expired.'


class TokenInvalid(APIException):
    status_code = 400
    default_detail = 'Invalid token.'


class PasswordsNotMatch(APIException):
    status_code = 400
    default_detail = 'Passwords not match.'


def custom_exception_handler(exc, context):
    """
    REST_FRAMEWORK settings, EXCEPTION_HANDLER.
    Add additional info to response.
    """
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(exc, TokenExpired) or isinstance(exc, TokenInvalid):
            response.data['error_code'] = 'Bad Token'

        if isinstance(exc, PasswordsNotMatch):
            response.data.pop('detail')
            response.data['new_password2'] = ['Incorrect']

    return response
