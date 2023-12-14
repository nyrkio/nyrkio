#!/bin/sh
set -e
. /venv/bin/activate

ls /usr/src/app
exec uvicorn api.api:app --proxy-headers --host 0.0.0.0 --port 80