#
# Notice: Keep this file in sync with Dockerfile.arm32v7
#

FROM python:3.7-slim-stretch

LABEL maintainer="Dennis Muth <d.muth@gmx.net>"

# See below for BUILD ARG 'INSTALL_DEV_PACKAGES'
# ARG INSTALL_DEV_PACKAGES="no"

ENV CONFDIR=/config \
    DEBIAN_FRONTEND="noninteractive" \
    LOGDIR=/logs \
    PNP_LOG_CONF=/config/logging.yaml \
    PYTHONPATH=/pnp \
    WORKDIR=/pnp

# Volumes
VOLUME ${CONFDIR}
VOLUME ${LOGDIR}

# Create directory structure
RUN mkdir -p ${WORKDIR} && \
    mkdir -p ${CONFDIR} && \
    mkdir -p ${LOGDIR}

WORKDIR ${WORKDIR}

# Copy build scripts
COPY docker/ docker/
RUN docker/setup_prereqs

# Create requirements.txt from poetry
COPY README.md pyproject.toml poetry.lock ./

RUN poetry export \
        --without-hashes \
        -E "dropbox fitbit fritz fswatcher ftp gmail http-server miflora pushbullet" \
        -f requirements.txt \
        > requirements.txt && \
    pip3 install \
        --no-cache-dir \
        -r requirements.txt

COPY . .

RUN poetry build && \
    pip3 install \
        --no-cache-dir \
        "dist/$(poetry version | tr ' ' '-')-py3-none-any.whl"

CMD ["pnp", "/config/config.yaml"]
