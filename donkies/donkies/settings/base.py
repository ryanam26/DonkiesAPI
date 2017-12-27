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

DWOLLA_ID_DEV = data['DWOLLA_ID_DEV']
DWOLLA_SECRET_DEV = data['DWOLLA_SECRET_DEV']
DWOLLA_ID_PROD = data['DWOLLA_ID_PROD']
DWOLLA_SECRET_PROD = data['DWOLLA_SECRET_PROD']

DWOLLA_ID_SANDBOX = 'mr4MDycwRBAKz625eATwnTP1TeBme7h8IRzH8y2fLCXaBFuuGU'
DWOLLA_SECRET_SANDBOX = 'TGAVK07pW4vwbgsoiwXDnQmigGw3agVWSZG3GtlW0259tfSO66'

DWOLLA_ID_PROD = 'MqZLStTYuA2KTf4RqUYaYakjCwQ6SFCoFXrYJHiVefuVzUxuLJ'
DWOLLA_SECRET_PROD = 'mWx6GYpq2LONIK7kp72phVCerbUuaOPgD2ekX5VPjPXDOyHC0j'

FACEBOOK_APP_ID = data['FACEBOOK_APP_ID']
FACEBOOK_APP_SECRET = data['FACEBOOK_APP_SECRET']
FACEBOOK_REDIRECT_URI = data['FACEBOOK_REDIRECT_URI']

SPARKPOST_APIKEY = data['SPARKPOST_APIKEY']
SPARKPOST_FROM_EMAIL = data['SPARKPOST_FROM_EMAIL']

PLAID_CLIENT_ID = data['PLAID_CLIENT_ID']
PLAID_SECRET = data['PLAID_SECRET']
PLAID_PUBLIC_KEY = data['PLAID_PUBLIC_KEY']

STRIPE_TEST_SECRET_KEY = data['STRIPE_TEST_SECRET_KEY']
STRIPE_TEST_PUBLISHABLE_KEY = data['STRIPE_TEST_PUBLISHABLE_KEY']
STRIPE_LIVE_SECRET_KEY = data['STRIPE_LIVE_SECRET_KEY']
STRIPE_LIVE_PUBLISHABLE_KEY = data['STRIPE_LIVE_PUBLISHABLE_KEY']

BACKEND_DOMAIN = 'api.donkies.co'
BACKEND_URL = 'https://api.donkies.co'
FRONTEND_DOMAIN = 'app.donkies.co'
FRONTEND_URL = 'https://app.donkies.co'

DWOLLA_PROCESSOR_TOKEN_CREATE = 'https://sandbox.plaid.com/processor/dwolla/processor_token/create'
DWOLLA_TEMP_BUSINESS_ACCOUNT = 'https://api-uat.dwolla.com/funding-sources/6f9038e7-b7ba-4ef1-a43f-f919703a2d79'

# secret hash genereted from word - donkiesv1  hashlib.md5()
SALT = 'e01cb7c3ed0975ea229b75b6111896ce'

# Admin email for sending alerts
ALERTS_EMAIL = 'ryan@donkies.co'

AUTH_USER_MODEL = 'web.User'
APPEND_SLASH = False

DEFAULT_FROM_EMAIL = 'noreply@donkies.co'
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
    'rest_framework_swagger',
    'corsheaders',
    'web',
    'finance',
    'bank',
    'ach',
    'django_extensions',
    'recaptcha',
)

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
    'OPERATIONS_SORTER': 'alpha',
}

LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'

MIDDLEWARE = (
    'web.middleware.AccessControlMiddleware',
    'web.middleware.CaptureAuthenticationMiddleware',
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
                'django.contrib.messages.context_processors.messages'
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

MEDIA_ROOT = BASE_DIR + '/static/media/'
STATIC_URL = '/static/'
MEDIA_URL = '/static/media/'

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

FILE_UPLOAD_TEMP_DIR = MEDIA_ROOT + 'tmp/'

# STATICFILES_DIRS = [join(BASE_DIR, 'static')]

STATIC_ROOT = join(BASE_DIR, 'static')

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
        # 'rest_framework.renderers.BrowsableAPIRenderer'
    ),
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        # 'rest_framework.parsers.FormParser',
        # 'rest_framework.parsers.MultiPartParser'
    ],
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
    'disable_existing_loggers': False,

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
        },

        'console': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        }
    }
}

# Custom token auth.
TOKEN_EXPIRE_MINUTES = 1400

REDIS_DB = redis.StrictRedis(host='127.0.0.1', port=6379, db=2)

# Plaid API mode production/development/sandbox
PLAID_ENV = 'development'

# Plaid webhook url.
PLAID_WEBHOOKS_URL = BACKEND_URL + '/v1/plaid/webhooks'

# The list of products for Plaid Link.
# Institutions, that don't have these products,
# are not showed in the Plaid Link.
PLAID_LINK_PRODUCTS = ['auth', 'transactions']

# The name that is showed on Plaid Link.
PLAID_LINK_CLIENT_NAME = 'Donkies LLC'

# Dwolla API mode PROD/DEV
DWOLLA_API_MODE = 'DEV'

# Stripe API Mode PROD/DEV
STRIPE_API_MODE = 'DEV'


# Donkies LLC email in Dwolla to receive transfers.
DONKIES_DWOLLA_EMAIL_DEV = 'vladigris@gmail.com'
DONKIES_DWOLLA_EMAIL_PROD = 'bank@donkies.co'

# Minimum transfer amount for collected roundup.
# As soon as user reach that amount - send transfer to Donkies in Dwolla.
TRANSFER_TO_DONKIES_MIN_AMOUNT = 5

# Minimum transfer amount for collected roundup.
TRANSFER_TO_STRIPE_MIN_AMOUNT = 5

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
