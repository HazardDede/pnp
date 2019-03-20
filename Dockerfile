#
# Notice: Keep this file in sync with Dockerfile.arm32v7
#

FROM python:3.5-slim-stretch

LABEL maintainer="Dennis Muth <d.muth@gmx.net>"

# See below for BUILD ARG 'INSTALL_DEV_PACKAGES'
# ARG INSTALL_DEV_PACKAGES="no"

ENV CONFDIR=/config \
    DEBIAN_FRONTEND="noninteractive" \
    LOGDIR=/logs \
    PNP_LOG_CONF=${CONFDIR}/logging.yaml \
    PYTHONPATH=${WORKDIR} \
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

# Copy setup.py and dependants
COPY README.md setup.py ./

RUN pip3 install \
    --no-cache-dir \
    .[dropbox,fitbit,fswatcher,gmail,http-server,miflora,pushbullet]

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