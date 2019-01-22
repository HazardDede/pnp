FROM python:3.5-slim-stretch

ENV WORKDIR=/pnp
ENV CONFDIR=/config
ENV PNP_LOG_CONF=${CONFDIR}/logging.yaml
ENV LOGDIR=/logs

RUN apt-get update -yy && \
    apt-get install -yy gcc

RUN mkdir -p ${WORKDIR} && \
    mkdir -p ${CONFDIR} && \
    mkdir -p ${LOGDIR}

COPY . ${WORKDIR}

RUN cd ${WORKDIR} && \
    pip3 install \
        --process-dependency-links \
        .[dropbox,fitbit,fswatcher,gmail,http-server,pushbullet]

VOLUME ${CONFDIR}
VOLUME ${LOGDIR}

CMD ["pnp", "/config/config.yaml"]