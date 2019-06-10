#!/bin/bash

docker-compose -f docker-compose-DEV.yml run --rm web-dev python manage.py db upgrade
docker-compose -f docker-compose-DEV.yml down