#!/usr/bin/env bash

pip install -r requirements.txt

echo Python Version ${TRAVIS_PYTHON_VERSION}

if [ "${TRAVIS_PYTHON_VERSION}" != '3.5' ]; then
    pip install -e .[fritz]
fi

if [ "${TRAVIS_EVENT_TYPE:-none}" == 'cron' ]; then
    pip install -e .[faceR]
fi