#!/usr/bin/env bash

pip install -r requirements.txt
if [ "${TRAVIS_EVENT_TYPE:-none}" == 'cron' ]; then
    pip install -e .[faceR]
fi