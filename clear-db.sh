#!/bin/sh

cd $(dirname $0)
source ./venv_check.sh

python -m job_tracker.backend.cli truncate-db
