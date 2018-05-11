FROM python:3.6-slim-stretch

ENV WORKDIR=/tmp/pnp
ENV CONFDIR=/config

COPY . ${WORKDIR}

RUN cd ${WORKDIR} && \
    pip3 install .

VOLUME /config

CMD ["pnp", "/config/config.json"]