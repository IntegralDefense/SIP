#!/bin/bash

docker-compose -f docker-compose-DEV.yml build
docker-compose -f docker-compose-PROD.yml up -d > /dev/null

until $(curl --silent --head --insecure --request GET https://127.0.0.1:443 | grep "302 FOUND" > /dev/null); do
    echo "Waiting for SIP (PROD) to start..."
    sleep 1
done