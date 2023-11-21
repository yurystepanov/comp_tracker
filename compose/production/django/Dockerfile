# Pull official base Python Docker image
FROM python:3.10.7

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# COPY entrypoint
COPY ./compose/production/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# COPY start scripts
COPY ./compose/production/django/start /start
RUN chmod +x /start

COPY ./compose/production/django/celery/worker/start /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./compose/production/django/celery/beat/start /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./compose/production/django/celery/flower/start /start-flower
RUN chmod +x /start-flower

COPY ./compose/production/django/telegram_bot/start /start-telegrambot
RUN chmod +x /start-telegrambot

#COPY config files
COPY ./compose/production/django/uwsgi /config/uwsgi
COPY ./compose/production/nginx /config/nginx

# Set work directory
WORKDIR /code

# Copy the Django project
COPY . /code/

ENTRYPOINT ["/entrypoint.sh"]