#
# Notice: Keep this file in sync with Dockerfile
#

FROM arm32v7/python:3.5-slim-stretch
COPY qemu-arm-static /usr/bin

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
RUN docker/setup_prereqs.arm

# Copy setup.py and dependants
COPY README.md setup.py requirements.dev ./

RUN pip3 install \
    --no-cache-dir \
    --extra-index-url https://www.piwheels.hostedpi.com/simple \
    .[dht,dropbox,fitbit,fswatcher,ftp,gmail,gpio,http-server,miflora,pushbullet]

COPY . .

# Run the installation routine again to register entry points properly
RUN pip3 install \
    --no-cache-dir \
    .

# Changing 'INSTALL_DEV_PACKAGES' has no effect on previous layers, but will force a recreation
# Use the build arg in the last possible moment
ARG INSTALL_DEV_PACKAGES="no"
RUN test "${INSTALL_DEV_PACKAGES}" = "yes" \
    && pip3 install --no-cache-dir -r requirements.dev \
    || rm -rf tests/ requirements.dev docker

CMD ["pnp", "/config/config.yaml"]
