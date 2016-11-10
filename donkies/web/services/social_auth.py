from django.shortcuts import redirect


def save_user_facebook(backend, user, response, *args, **kwargs):
    if backend.name != 'facebook':
        return
    print('response', response)
    print('backend', backend)
    print('user', user)
    return redirect('/')  # redirect to frontend url with token


def save_user_google(backend, user, response, *args, **kwargs):
    pass
