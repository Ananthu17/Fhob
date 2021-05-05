"""
Django settings for film_hobo project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
import environ
from pathlib import Path

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!

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

    # project apps
    'initial_user',
    'hobo_user',
    'payment',

    'bootstrap_datepicker_plus',
    'django_select2',
    'crispy_forms',
    'django_s3_storage',
    'zappa_django_utils'
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

SITE_ID = 1

MIDDLEWARE = [
    # 'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ],
    'DATE_INPUT_FORMATS': ["%Y-%m-%d"],
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
EMAIL_FROM = os.environ.get(
    'AUTHEMAIL_DEFAULT_EMAIL_FROM', 'avin@techversantinfo.com')
EMAIL_HOST_USER = os.environ.get(
    'AUTHEMAIL_EMAIL_HOST_USER', 'avin@techversantinfo.com')
EMAIL_HOST_PASSWORD = os.environ.get(
    'AUTHEMAIL_EMAIL_HOST_PASSWORD', 'avinpython19')
EMAIL_BCC = os.environ.get(
    'AUTHEMAIL_DEFAULT_EMAIL_BCC', '')

OLD_PASSWORD_FIELD_ENABLED = True

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
