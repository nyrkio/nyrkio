FROM python:3.8.6-slim as base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1

# set work directory
WORKDIR /usr/src/backend

###########
# BUILDER #
###########

# pull official base image
FROM base as builder

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev libc-dev

# lint
RUN pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"

RUN python -m venv /venv

COPY . .
RUN poetry export --no-hashes -f requirements.txt | /venv/bin/pip install -r /dev/stdin

RUN poetry build
RUN /venv/bin/pip install dist/*.whl

#########
# FINAL #
#########

FROM base as final

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat libpq-dev

# create the app user
RUN addgroup --system app && adduser --system --group app

COPY --from=builder /venv /venv

COPY ./entrypoint.sh ./

# copy project
COPY --chown=app:app . ./

# change to the app user
USER app

CMD ["/usr/src/backend/entrypoint.sh"]
