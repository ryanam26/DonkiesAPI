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


FACEBOOK_APP_ID = '1825754931027785'
FACEBOOK_APP_SECRET = '8f19d96855a9295c06271f6c9e26ae20'
FACEBOOK_REDIRECT_URI = 'http://donkies.com:8080/login_facebook'

ATRIUM_API_MODE = 'DEV'
