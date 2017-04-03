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


FACEBOOK_APP_ID = '288669701548593'
FACEBOOK_APP_SECRET = 'e8c6cebdc6a276f9bdcd11e18716a951'
FACEBOOK_REDIRECT_URI = 'http://donkies.com:8080/login_facebook'

ATRIUM_API_MODE = 'DEV'
PLAID_ENV = 'sandbox'
