FROM astral/uv:python3.13-alpine AS base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

###########
# BUILDER #
###########



# pull uv base image
# FROM base as builder



RUN apk add --no-cache git
RUN apk add --no-cache build-base

# Copy the project into the image
COPY . /backend

RUN pwd
RUN ls

# Disable development dependencies
ENV UV_NO_DEV=1

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /backend
RUN pwd
RUN ls


RUN uv sync --locked

# Presuming there is a `my_app` command provided by the project
CMD ["uv", "run", "uvicorn backend.api.api:app --proxy-headers --host 0.0.0.0 --port $API_PORT --log-level info"]
