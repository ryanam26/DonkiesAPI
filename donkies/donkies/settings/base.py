import json
import os
import redis
from os.path import abspath, join, dirname

BASE_DIR = abspath(join(dirname(abspath(__file__)), '..', '..', '..'))

data_path = os.path.join(BASE_DIR, 'donkies/donkies/settings/data.json')
data = json.loads(open(data_path).read())

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/social_login/'

ALLOWED_HOSTS = data['ALLOWED_HOSTS']
SECRET_KEY = data['SECRET_KEY']
DB_NAME = data['DB_NAME']
DB_USER = data['DB_USER']
DB_PASSWORD = data['DB_PASSWORD']
DB_HOST = data['DB_HOST']
SERVER_IP = data['SERVER_IP']

ATRIUM_CLIENT_ID_PROD = data['ATRIUM_CLIENT_ID_PROD']
ATRIUM_KEY_PROD = data['ATRIUM_KEY_PROD']
ATRIUM_CLIENT_ID_DEV = data['ATRIUM_CLIENT_ID_DEV']
ATRIUM_KEY_DEV = data['ATRIUM_KEY_DEV']

DWOLLA_ID_DEV = data['DWOLLA_ID_DEV']
DWOLLA_SECRET_DEV = data['DWOLLA_SECRET_DEV']
DWOLLA_ID_PROD = data['DWOLLA_ID_PROD']
DWOLLA_SECRET_PROD = data['DWOLLA_SECRET_PROD']

FACEBOOK_APP_ID = data['FACEBOOK_APP_ID']
FACEBOOK_APP_SECRET = data['FACEBOOK_APP_SECRET']
FACEBOOK_REDIRECT_URI = data['FACEBOOK_REDIRECT_URI']

BACKEND_DOMAIN = 'api.donkies.co'
BACKEND_URL = 'http://api.donkies.co'
FRONTEND_DOMAIN = 'donkies.co'
FRONTEND_URL = 'http://donkies.co'

AUTH_USER_MODEL = 'web.User'
APPEND_SLASH = False

DEFAULT_FROM_EMAIL = 'noreply@domain.com'
EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'social.apps.django_app.default',
    # 'oauth2_provider',
    'corsheaders',
    'web',
    'finance',
    'bank'
)

MIDDLEWARE = (
    'web.middleware.AccessControlMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'web.middleware.ActiveUserMiddleware'
)

ROOT_URLCONF = 'donkies.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'donkies.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = BASE_DIR + '/static/static/media/'
STATIC_URL = '/static/'
MEDIA_URL = '/static/media/'

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

FILE_UPLOAD_TEMP_DIR = MEDIA_ROOT + 'tmp/'

STATICFILES_DIRS = [join(BASE_DIR, 'static/static')]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope'
    }
}

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
    'social.backends.twitter.TwitterOAuth',
    'django.contrib.auth.backends.ModelBackend',
)

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_PERMISSION_CLASSES': (),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'donkies.authentication.BasicAuthentication',
        'donkies.authentication.SessionAuthentication',
        'donkies.authentication.TokenAuthentication',
        # 'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S',
    'EXCEPTION_HANDLER': 'web.exceptions.custom_exception_handler'
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },

    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d \
            %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },

    'handlers': {
        'console': {
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'db': {
            'class': 'donkies.loggers.MyDbLogHandler',
            'formatter': 'verbose'
        }
    },

    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': True,
        },

        'django.request': {
            'handlers': ['db'],
            'level': 'ERROR',
            'propagate': False,
        },

        'app': {
            'level': 'DEBUG',
            'handlers': ['console', 'db'],
            'propagate': False,
        },

        'dwolla': {
            'level': 'DEBUG',
            'handlers': ['console', 'db'],
            'propagate': False,
        }
    }
}

# Custom token auth.
TOKEN_EXPIRE_MINUTES = 1400

REDIS_DB = redis.StrictRedis(host='127.0.0.1', port=6379, db=2)

# Atrium API mode PROD/DEV
ATRIUM_API_MODE = 'DEV'

# Dwolla API mode PROD/DEV
DWOLLA_API_MODE = 'DEV'

# Donkies LLC email in Dwolla to receive transfers.
DONKIES_DWOLLA_EMAIL_DEV = 'vladigris@gmail.com'
DONKIES_DWOLLA_EMAIL_PROD = 'bank@donkies.co'

# Users for real tests.
TEST_USERS = [
    {
        'email': 'test@donkies.co',
        'guid': 'USR-f4bc90ba-4504-6fda-b07c-5aa965832a06',
        'password': '111',
        'first_name': 'Vladimir',
        'last_name': 'Grischenko'
    },
    {
        'email': 'alex@donkies.co',
        'guid': 'USR-bd2621a6-bdcb-c671-3079-f3ad8cd2b501',
        'password': '111',
        'first_name': 'Alex',
        'last_name': 'Arias'
    },
]

US_STATES = (
    ('AL', 'Alabama'),
    ('AK', 'Alaska'),
    ('AZ', 'Arizona'),
    ('AR', 'Arkansas'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DE', 'Delaware'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('IA', 'Iowa'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('ME', 'Maine'),
    ('MD', 'Maryland'),
    ('MA', 'Massachusetts'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MS', 'Mississippi'),
    ('MO', 'Missouri'),
    ('MT', 'Montana'),
    ('NE', 'Nebraska'),
    ('NV', 'Nevada'),
    ('NH', 'New Hampshire'),
    ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'),
    ('NY', 'New York'),
    ('NC', 'North Carolina'),
    ('ND', 'North Dakota'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PA', 'Pennsylvania'),
    ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'),
    ('SD', 'South Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VT', 'Vermont'),
    ('VA', 'Virginia'),
    ('WA', 'Washington'),
    ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'),
    ('WY', 'Wyoming')
)
