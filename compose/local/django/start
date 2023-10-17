#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Copy NGINX config
cp -r /config/nginx/conf /active/config/nginx/
cp -r /config/nginx/ssl /active/config/nginx/

# Change current directory to ctraacker
cd ctracker || exit

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

#Run server
echo "Running uwsgi server"
uwsgi --ini /config/uwsgi/uwsgi.ini