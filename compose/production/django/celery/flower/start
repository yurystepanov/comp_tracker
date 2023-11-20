#!/bin/bash

set -o errexit
set -o nounset

# Change current directory to ctracker
cd ctracker || exit

worker_ready() {
    celery -A ctracker inspect ping
}

until worker_ready; do
  >&2 echo 'Celery workers not available'
  sleep 1
done
>&2 echo 'Celery workers is available'

celery -A ctracker  \
    --broker="${CELERY_BROKER}" \
    flower