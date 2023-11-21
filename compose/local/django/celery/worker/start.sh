#!/bin/bash

set -o errexit
set -o nounset

# Change current directory to ctracker
cd ctracker || exit

celery -A ctracker worker -l INFO