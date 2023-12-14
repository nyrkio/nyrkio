#!/bin/sh
#set -e
. /venv/bin/activate

cd /usr/src
exec uvicorn backend.api.api:app --proxy-headers --host 0.0.0.0 --port $API_PORT
