from .base import *

DEBUG = False

TEMPLATE_DEBUG = False


DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'safepod',
                'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
                'PORT': '5432',
                'USER': get_secret_key("DB_USERNAME"),
                'PASSWORD': get_secret_key("DB_PASSWORD"),
                 }
            }

ALLOWED_HOSTS = ['safepodapp.org']
    
GOOGLE_ANALYTICS_PROPERTY_ID = get_secret_key('GOOGLE_ANALYTICS_PROPERTY_ID')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/abhay/logs/django/safepod.debug.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'safepod': {
            'handlers': ['file'],
            'level': 'DEBUG',
        }
    }
}
