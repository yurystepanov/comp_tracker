# Pull official base Python Docker image
FROM python:3.10.7

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN pip install --upgrade pip setuptools

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# COPY entrypoint
COPY ./compose/production/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# COPY start scripts
COPY ./compose/production/django/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./compose/production/django/celery/worker/start.sh /start-celeryworker.sh
RUN chmod +x /start-celeryworker.sh

COPY ./compose/production/django/celery/beat/start.sh /start-celerybeat.sh
RUN chmod +x /start-celerybeat.sh

COPY ./compose/production/django/celery/flower/start.sh /start-flower.sh
RUN chmod +x /start-flower.sh

COPY ./compose/production/django/telegram_bot/start.sh /start-telegrambot.sh
RUN chmod +x /start-telegrambot.sh

#COPY config files
COPY ./compose/production/django/uwsgi /config/uwsgi
COPY ./compose/production/nginx /config/nginx

# Set work directory
WORKDIR /code

# Copy the Django project
COPY . /code/

ENTRYPOINT ["/entrypoint.sh"]