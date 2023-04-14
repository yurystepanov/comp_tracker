#!/usr/bin/env bash

cp -r ./config/nginx ./data/

cd ctracker || exit

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

#Run server
echo "Running uwsgi server"
uwsgi --ini /code/config/uwsgi/uwsgi.ini