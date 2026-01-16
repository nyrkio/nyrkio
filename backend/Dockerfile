FROM astral/uv:python3.13-alpine AS base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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


COPY . .

RUN uv build


#########
# FINAL #
#########

FROM base as final

# create the app user
RUN addgroup --system app && adduser --system --group app

COPY ./entrypoint.sh ./

# Copy GitHub app private key
COPY ./keys/ /usr/src/backend/keys/

# copy project
COPY --chown=app:app . ./

# change to the app user
USER app

CMD ["/usr/src/backend/entrypoint.sh"]
