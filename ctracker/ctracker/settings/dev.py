from .base import *
import os

DEBUG = os.environ.get('DEBUG')


# Security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

ADMINS = [
    ('Yury Stepanov', 'yury.a.stepanov@gmail.com'),
]

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'ctracker.ru']

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('SQL_ENGINE'),
        'NAME': os.environ.get('SQL_DATABASE'),
        'USER': os.environ.get('SQL_USER'),
        'PASSWORD': os.environ.get('SQL_PASSWORD'),
        "HOST": os.environ.get('SQL_HOST'),
        "PORT": os.environ.get('SQL_PORT'),
    }
}

TELEGRAM_BOT_API_KEY = os.environ.get('TG_BOT_API_KEY')
