#!/usr/bin/env bash

pip install poetry

echo Python Version ${TRAVIS_PYTHON_VERSION}

if [ "${TRAVIS_PYTHON_VERSION}" != '3.5' ]; then
    poetry install -E "dropbox fitbit fritz fswatcher ftp gmail http-server miflora pushbullet sound"
else
    poetry install -E "dropbox fitbit fswatcher ftp gmail http-server miflora pushbullet sound"
fi

if [ "${TRAVIS_EVENT_TYPE:-none}" == 'cron' ]; then
    pip install -e .[faceR]
fi