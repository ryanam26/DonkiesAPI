from .base import *

DEBUG = True
PRODUCTION = False
TESTING = False

# MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
# INSTALLED_APPS += ('debug_toolbar.apps.DebugToolbarConfig',)

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

DEBUG_TOOLBAR_CONFIG = {
    'EXCLUDE_URLS': ('/admin',),
    'INTERCEPT_REDIRECTS': False,
}

INTERNAL_IPS = ('127.0.0.1',)

FACEBOOK_APP_ID = '1904721553101930'
FACEBOOK_APP_SECRET = 'a9b816192ca8b9fc454b6eeb76d0b459'
FACEBOOK_REDIRECT_URI = 'http://donkies.com:8080/login_facebook'

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

DONKIES_MODE = 'development'

PLAID_ENV = 'sandbox'
# PLAID_ENV = 'development'
DWOLLA_ENV = 'sandbox'
# DWOLLA_ENV = 'production'

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'postmaster@sandbox2824da8569374d539e23a393d242455e.mailgun.org'
EMAIL_HOST_PASSWORD = '9fdc14104071f71ed1c7f522a4ed5b41'
EMAIL_USE_TLS = True
BROKER_URL = 'redis://donkies-redis:6379/0'
REDIS_DB = redis.StrictRedis(host='donkies-redis', port=6379, db=2)
LOGGING['loggers']['django.request']['handlers'] += ['console']
