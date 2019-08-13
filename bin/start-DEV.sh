#!/bin/bash

docker-compose -f docker-compose-DEV.yml build
docker-compose -f docker-compose-DEV.yml up -d > /dev/null

until $(curl --noproxy 127.0.0.1 --silent --head --insecure --request GET https://127.0.0.1:4443 | grep "302 FOUND" > /dev/null); do
    echo "Waiting for SIP (DEV) to start..."
    sleep 1
done
