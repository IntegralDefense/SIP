#!/bin/bash

docker-compose -f docker-compose-DEV.yml run --rm web-dev python manage.py db init
docker-compose -f docker-compose-DEV.yml down