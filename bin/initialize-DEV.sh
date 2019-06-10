#!/bin/bash

docker-compose -f docker-compose-DEV.yml up -d > /dev/null

until $(curl --silent --head --insecure --request GET https://127.0.0.1:4443 | grep "302 FOUND" > /dev/null); do
    echo "Waiting for SIP (DEV) to start..."
    sleep 1
done

docker-compose -f docker-compose-DEV.yml down > /dev/null
docker-compose -f docker-compose-DEV.yml run web-dev python manage.py setupdb --yes > /dev/null
docker-compose -f docker-compose-DEV.yml run web-dev python manage.py seeddb
docker-compose -f docker-compose-DEV.yml down > /dev/null