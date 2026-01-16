FROM python:3.13-slim AS base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /usr/src

###########
# BUILDER #
###########

# pull official base image
FROM base as builder

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev libc-dev


COPY . .

WORKDIR /usr/src/backend

RUN pip install --upgrade pip
RUN pip install "uv==0.9.2"
RUN uv build
RUN uv pip install

#########
# FINAL #
#########

FROM base as final

# create the app user
RUN addgroup --system app && adduser --system --group app

COPY --from=builder /venv /venv

COPY ./entrypoint.sh ./

# Copy GitHub app private key
COPY ./keys/ /usr/src/backend/keys/

# copy project
COPY --chown=app:app . ./

# change to the app user
USER app

CMD ["/usr/src/backend/entrypoint.sh"]
