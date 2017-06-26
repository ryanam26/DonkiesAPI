from .base import *

DEBUG = True
PRODUCTION = False
TESTING = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': '5432'
    }
}


FACEBOOK_APP_ID = '1904721553101930'
FACEBOOK_APP_SECRET = 'a9b816192ca8b9fc454b6eeb76d0b459'
FACEBOOK_REDIRECT_URI = 'http://donkies.com:8080/login_facebook'

PLAID_ENV = 'sandbox'
