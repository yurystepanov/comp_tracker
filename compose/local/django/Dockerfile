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
COPY ./compose/local/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# COPY start scripts
COPY ./compose/local/django/start /start
RUN chmod +x /start

COPY ./compose/local/django/celery/worker/start /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./compose/local/django/celery/beat/start /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./compose/local/django/celery/flower/start /start-flower
RUN chmod +x /start-flower

COPY ./compose/local/django/telegram_bot/start /start-telegrambot
RUN chmod +x /start-telegrambot

#COPY config files
COPY ./compose/local/django/uwsgi /config/uwsgi
COPY ./compose/local/nginx /config/nginx

# Set work directory
WORKDIR /code

# Copy the Django project
COPY . /code/

ENTRYPOINT ["/entrypoint.sh"]