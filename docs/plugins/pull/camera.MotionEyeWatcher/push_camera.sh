#!/bin/bash

# Contents of push_camera.sh

IMAGE_FILE=$1

curl -X POST -F "image=@${IMAGE_FILE}" ${HA_HOST}/api/webhook/motion01