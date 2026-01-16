#!/bin/sh
#set -e

cd /usr/src/backend
uv run uvicorn api.api:app --proxy-headers --host 0.0.0.0 --port $API_PORT --log-level info
