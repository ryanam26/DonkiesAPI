"""
Old implementation.
Not used.
"""

from django.shortcuts import redirect
from django.conf import settings
from web.models import User


def save_user_facebook(backend, user, response, *args, **kwargs):
    if backend.name != 'facebook':
        return None
    result = User.objects.login_facebook(response)
    if 'message' in result:
        url = settings.FACEBOOK_FAIL_URL + '?message={}'.format(
            result['message'])
        return redirect(url)

    url = settings.FACEBOOK_SUCCESS_URL + '?token={}'.format(
        result['token'])
    return redirect(url)


def save_user_google(backend, user, response, *args, **kwargs):
    pass
