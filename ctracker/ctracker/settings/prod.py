from .base import *
import os

DEBUG = False

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

ADMINS = [
    ('Yury Stepanov', 'yury.a.stepanov@gmail.com'),
]

ALLOWED_HOSTS = ['ctracker.ystep.ru', 'www.ctracker.ystep.ru']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    }
}

TELEGRAM_BOT_API_KEY = os.environ.get('TG_BOT_API_KEY')
