"""
Django settings for untitled_oj project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#TEMPLATE_DIR = '/static/templates/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '882u75b38hem^@ov&4y9(zlmn+a!d5bpmy%^4k&tqm416$-4*c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'disqus',
    'pagination',
    'handle',
    'problemset',
    'contest',
    'submission',
    'index',
    'administrate',
    'rank',
    'course',
    'ojutility',
    'taggit',
    'stars',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'untitled_oj.urls'

WSGI_APPLICATION = 'untitled_oj.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'onlinejudge',
        'USER': 'dbuser',
        'PASSWORD': 'password',
        'HOST': '',
        'PORT': '',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-tw'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), '../static/').replace('\\','/'),
)

TEMPLATE_DIRS = (
    BASE_DIR+'/static/templates',
)

TEMPLATE_CONTEXT_PROCESSORS=(
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
)

#The directory path which contains the test data.
TESTDATA_DIR = ''

DISQUS_API_KEY = 'Vg4FoMkhG6Wr8DKhLxYFznq5gMKlCMKH9K8KDUB8QiIRzoWnejgwWLKsYrRVpnTl'
DISQUS_WEBSITE_SHORTNAME = 'untitledoj'
