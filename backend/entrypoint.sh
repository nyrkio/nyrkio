#!/bin/sh
#set -e

cd /
pwd
ls -laiFh
ls -laiFh /backend
ls -laiFh /.venv || /bin/true
ls -laiFh /backend/.venv || /bin/true

uv run uvicorn backend.api.api:app --proxy-headers --host 0.0.0.0 --port $API_PORT --log-level info
