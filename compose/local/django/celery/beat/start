#!/bin/bash

set -o errexit
set -o nounset

# Change current directory to ctracker
cd ctracker || exit

rm -f './celerybeat.pid'
celery -A ctracker beat -l INFO