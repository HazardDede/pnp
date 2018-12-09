FROM python:3.6-slim-stretch

ENV WORKDIR=/pnp
ENV CONFDIR=/config
ENV PNP_LOG_CONF=${CONFDIR}/logging.yaml
ENV LOGDIR=/logs

RUN apt-get update -yy && \
    apt-get install -yy gcc \
                        git

RUN mkdir -p ${WORKDIR} && \
    mkdir -p ${CONFDIR} && \
    mkdir -p ${LOGDIR}

COPY . ${WORKDIR}

RUN cd ${WORKDIR} && \
    pip3 install --process-dependency-links .[dropbox,fswatcher,http-server,pushbullet]

VOLUME ${CONFDIR}
VOLUME ${LOGDIR}

CMD ["pnp", "/config/config.yaml"]