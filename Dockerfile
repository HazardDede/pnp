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
        -E "dropbox" -E "fitbit" -E "fritz" -E "fswatcher" \
        -E "ftp" -E "gmail" -E "miflora" -E "pushbullet" \
        -E "speedtest" \
        -f requirements.txt \
        > requirements.txt && \
    pip3 install \
        --no-cache-dir \
        -r requirements.txt

COPY . .

CMD ["python3", "-m", "pnp", "/config/config.yaml"]
