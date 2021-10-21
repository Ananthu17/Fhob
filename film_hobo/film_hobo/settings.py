"""
Django settings for film_hobo project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from celery.schedules import crontab
import environ
import os
from pathlib import Path
from corsheaders.defaults import default_headers
import film_hobo.tasks

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!

# PROJECT_ENVIRONMENT valid options
# 1 - LOCAL
# 2 - DEMO_SERVER
# 3 - AWS_PRODUCTION

PROJECT_ENVIRONMENT = "LOCAL"
# PROJECT_ENVIRONMENT = "DEMO_SERVER"


if PROJECT_ENVIRONMENT == "DEMO_SERVER":
    DEBUG = False
    # ORIGIN_URL = "http://202.88.246.92:8041"
    # ORIGIN_URL = "http://172.19.0.3:8041"
    ORIGIN_URL = "http://app:8041"
    # demo server database credentials
    DATABASES = {
        'default': {
            'ENGINE': env("DEMO_SERVER_DATABASE_ENGINE"),
            'NAME': env("DEMO_SERVER_DATABASE_NAME"),
            'USER': env("DEMO_SERVER_DATABASE_USER"),
            'PASSWORD': env("DEMO_SERVER_DATABASE_PASSWORD"),
            'HOST': env("DEMO_SERVER_DATABASE_HOST"),
            'PORT': env("DEMO_SERVER_DATABASE_PORT"),
        }
    }
    CELERY_BROKER_URL = 'redis://redis:6379'
    CELERY_RESULT_BACKEND = "redis://redis:6379"
    CELERY_BEAT_SCHEDULE = {
        "send_email_report": {
            "task": "film_hobo.tasks.send_email_report",
            "schedule": crontab(minute="*/1"),
        }
    }

elif PROJECT_ENVIRONMENT == "AWS_PRODUCTION":
    ORIGIN_URL = "http://www.filmhobo.com"
else:
    DEBUG = True
    ORIGIN_URL = "http://127.0.0.1:8000"
    # local database credentials
    DATABASES = {
        'default': {
            'ENGINE': env("DATABASE_ENGINE"),
            'NAME': env("DATABASE_NAME"),
            'USER': env("DATABASE_USER"),
            'PASSWORD': env("DATABASE_PASSWORD"),
            'HOST': env("DATABASE_HOST"),
            'PORT': env("DATABASE_PORT"),
        }
    }
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = "redis://localhost:6379"
    CELERY_BEAT_SCHEDULE = {
        "send_email_report": {
            "task": "film_hobo.tasks.send_email_report",
            "schedule": crontab(minute="*/1"),
        }
    }

# # for development
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1',
                 '5s3u3jnor6.execute-api.us-east-1.amazonaws.com',
                 '*']

# for production
# DEBUG = False

# ALLOWED_HOSTS = ['www.filmhobo.com',
#                  'filmhobo.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party packages
    'environ',
    'rest_auth',
    'rest_framework',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'rest_framework.authtoken',
    'import_export',
    'phonenumber_field',
    'authemail',
    'allauth.socialaccount',
    'django_filters',
    'django_social_share',
    # 'subscription',

    # project apps
    'initial_user',
    'hobo_user',
    'payment',
    'general',
    'project',
    'messaging',

    'bootstrap_datepicker_plus',
    'django_select2',
    'crispy_forms',
    'django_s3_storage',
    'zappa_django_utils',
    'channels',
    'paypal.standard.ipn',
    'corsheaders',
    'ckeditor',
    'ckeditor_uploader'
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # 'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'film_hobo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'film_hobo.wsgi.application'
# Channels
ASGI_APPLICATION = "film_hobo.asgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# # aws rds credentials
# DATABASES = {
#     'default': {
#         'ENGINE': env("AWS_DATABASE_ENGINE"),
#         'NAME': env("AWS_DATABASE_NAME"),
#         'USER': env("AWS_DATABASE_USER"),
#         'PASSWORD': env("AWS_DATABASE_PASSWORD"),
#         'HOST': env("AWS_DATABASE_HOST"),
#         'PORT': env("AWS_DATABASE_PORT"),
#         'OPTIONS': {
#             'connect_timeout': 5,
#         }
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ],
    'DATE_INPUT_FORMATS': ["%Y-%m-%d"],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ]
}


ACCOUNT_EMAIL_VERIFICATION = 'none'

AUTH_USER_MODEL = 'hobo_user.CustomUser'

# settings to remove 'username' field from django-allauth
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False

# ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# Email settings
AUTH_EMAIL_VERIFICATION = True
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587

EMAIL_FROM = env("AUTHEMAIL_DEFAULT_EMAIL_FROM")
EMAIL_HOST_USER = env("AUTHEMAIL_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("AUTHEMAIL_EMAIL_HOST_PASSWORD")
EMAIL_BCC = ''

OLD_PASSWORD_FIELD_ENABLED = True

SITE_URL = os.environ.get('SITE_URL', '')


# # production settings

# AWS_DEFAULT_ACL = None

# YOUR_S3_BUCKET = "film-hobo-static"

# STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"
# AWS_S3_BUCKET_NAME_STATIC = YOUR_S3_BUCKET

# # These next two lines will serve the static files directly
# # from the s3 bucket
# AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % YOUR_S3_BUCKET
# STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

# # OR...if you create a fancy custom domain for your static files use:
# # AWS_S3_PUBLIC_URL_STATIC = "https://static.zappaguide.com/"

# # AWS_S3_MAX_AGE_SECONDS_STATIC = "94608000"

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #      "hosts": [('127.0.0.1', 6379)],
        # }
        # 'ROUTING': 'notification_channels.routing.channel_routing',
    }
}
# PAYPAL SETTINGS
PAYPAL_SENDER_EMAIL = env("PAYPAL_SENDER_EMAIL")
PAYPAL_RECEIVER_EMAIL = env("PAYPAL_RECEIVER_EMAIL")
PAYPAL_TEST = True
PAYPAL_CLIENT_ID = env("PAYPAL_CLIENT_ID")
PAYPAL_SECRET_ID = env("PAYPAL_SECRET_ID")

PRODUCT_ID = env("PRODUCT_ID")
INDIE_PAYMENT_MONTHLY = env("INDIE_PAYMENT_MONTHLY")
INDIE_PAYMENT_YEARLY = env("INDIE_PAYMENT_YEARLY")

PRO_PAYMENT_MONTHLY = env("PRO_PAYMENT_MONTHLY")
PRO_PAYMENT_YEARLY = env("PRO_PAYMENT_YEARLY")

COMPANY_PAYMENT_MONTHLY = env("COMPANY_PAYMENT_MONTHLY")
COMPANY_PAYMENT_YEARLY = env("COMPANY_PAYMENT_YEARLY")


AWS_CLIENT_ID = env("AWS_CLIENT_ID")
AWS_CLIENT_SECRET = env("AWS_CLIENT_SECRET")
S3_BUCKET_NAME = "filmhobo-videos"

CORS_ORIGIN_ALLOW = True
CORS_ALLOWED_ORIGINS = (
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://0.0.0.0',
    'http://202.88.246.92:8041',
)


CORS_ALLOW_HEADERS = default_headers + (
    'Access-Control-Allow-Origin',
)

if DEBUG:
    BRAINTREE_PRODUCTION = False
else:
    BRAINTREE_PRODUCTION = True

BRAINTREE_MERCHANT_ID = env("BRAINTREE_MERCHANT_ID")
BRAINTREE_PUBLIC_KEY = env("BRAINTREE_PUBLIC_KEY")
BRAINTREE_PRIVATE_KEY = env("BRAINTREE_PRIVATE_KEY")

# SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# development
CORS_ORIGIN_ALLOW_ALL = True

# production
# CORS_ORIGIN_ALLOW_ALL = False
# CORS_ORIGIN_WHITELIST = (
#   'http://localhost:8000',
# )

BRAINTREE_PLAN_ID_INDIE_PAYMENT_MONTHLY = \
    env("BRAINTREE_PLAN_ID_INDIE_PAYMENT_MONTHLY")
BRAINTREE_PLAN_ID_INDIE_PAYMENT_YEARLY = \
    env("BRAINTREE_PLAN_ID_INDIE_PAYMENT_YEARLY")
BRAINTREE_PLAN_ID_PRO_PAYMENT_MONTHLY = \
    env("BRAINTREE_PLAN_ID_PRO_PAYMENT_MONTHLY")
BRAINTREE_PLAN_ID_PRO_PAYMENT_YEARLY = \
    env("BRAINTREE_PLAN_ID_PRO_PAYMENT_YEARLY")
BRAINTREE_PLAN_ID_COMPANY_PAYMENT_MONTHLY = \
    env("BRAINTREE_PLAN_ID_COMPANY_PAYMENT_MONTHLY")
BRAINTREE_PLAN_ID_COMPANY_PAYMENT_YEARLY = \
    env("BRAINTREE_PLAN_ID_COMPANY_PAYMENT_YEARLY")

X_FRAME_OPTIONS = 'SAMEORIGIN'

CKEDITOR_UPLOAD_PATH = "ckeditor"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-',
             'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock',
             'Cut', 'Copy', 'Paste', 'PasteText', 'RemoveFormat'],
            ['Undo', 'Redo'],
            ['Format', 'Styles', 'Font'],
        ],
        'width': 'auto',
        'height': 140,
        'margin-left': '10%',
    },
}

# tijptjik/django-paypal-subscription package settings
# SUBSCRIPTION_PAYPAL_SETTINGS = {
#     'bussiness': 'kselivan@filmhobo.com'
# }

# SUBSCRIPTION_PAYPAL_FORM = 'paypal.standard.forms.PayPalPaymentsForm'

# SUBSCRIPTION_GRACE_PERIOD = 0

DEFAULT_GENERAL_MAIL = env("DEFAULT_GENERAL_MAIL")
DEFAULT_TECHNICAL_MAIL = env("DEFAULT_TECHNICAL_MAIL")
DEFAULT_SERVICE_MAIL = env("DEFAULT_SERVICE_MAIL")
DEFAULT_ABUSE_MAIL = env("DEFAULT_ABUSE_MAIL")
DEFAULT_BUSINESS_MAIL = env("DEFAULT_BUSINESS_MAIL")

