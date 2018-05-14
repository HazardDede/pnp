FROM python:3.6-slim-stretch

ENV WORKDIR=/tmp/pnp
ENV CONFDIR=/config

RUN apt-get update -yy && \
    apt-get install -yy git

COPY . ${WORKDIR}

RUN cd ${WORKDIR} && \
    pip3 install --process-dependency-links .

VOLUME /config

CMD ["pnp", "/config/config.json"]