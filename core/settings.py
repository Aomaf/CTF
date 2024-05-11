# -*- encoding: utf-8 -*-


import os
from decouple import config
from unipath import Path
import traceback

BASE_DIR = Path(__file__).parent.parent #app/
CORE_DIR = Path(__file__).parent    #app/core/

SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')
#with open("/home/qupcljvd/secret_key.txt") as f: SECRET_KEY = f.read().strip()

DEBUG = True

#SECURE_SSL_REDIRECT = True
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True

#ALLOWED_HOSTS        = ['qupc.win', 'www.qupc.win', '162.254.33.224']
#ALLOWED_HOSTS        = ['*']
ALLOWED_HOSTS        = ['localhost', 'localhost:85', '127.0.0.1', config('SERVER', default='127.0.0.1')]
CSRF_TRUSTED_ORIGINS = ['http://localhost:85', 'http://127.0.0.1', 'https://' + config('SERVER', default='127.0.0.1')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.home',
    'mathfilters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]
        
ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "dashboard"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "index"  # Route defined in home/urls.py
TEMPLATE_DIR = os.path.join(BASE_DIR, "apps/templates")  # ROOT dir for templates
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
				'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {'ENGINE':'django.db.backends.sqlite3','NAME':'db.sqlite3',},
    #'default': {'ENGINE':'django.db.backends.mysql','NAME':'qupcljvd_qupc_win_main_db','USER':'qupcljvd_qupc_main_db_user','PASSWORD':'m=XksrFS{tab','HOST':'localhost','PORT':'3306','OPTIONS':{'sql_mode':'traditional'}}
}

# to be put inside databases: 'init_command': 'ALTER DATABASE qupcljvd_qupc_main_db CHARACTER SET utf8_bin COLLATE utf8_general_ci'

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator' },
]

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Etc/GMT-3'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = ( os.path.join(BASE_DIR, 'apps/static'), )
STATIC_ROOT = os.path.join(BASE_DIR, 'static') # for production

#print("BASE_DIR: ", BASE_DIR)
#print("CORE_DIR: ", CORE_DIR)
#print("STATIC_ROOT: ", STATIC_ROOT)
#print("STATICFILES_DIRS: ", STATICFILES_DIRS)

# Email configuration gmail
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'qupc.win@gmail.com'
EMAIL_HOST_PASSWORD = 'fvbjnoknoansdlcx'
EMAIL_PORT = 587